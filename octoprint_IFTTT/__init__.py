# coding=utf-8
from __future__ import absolute_import

import octoprint
import requests

class IFTTTplugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.EventHandlerPlugin,
):
    def on_after_startup(self):
        self._storage_interface = self._file_manager._storage("local")

    def on_event(self, event_name, event_payload):
        events = self._settings.get(["events"])
        default_prefixes = self._settings.get(["default_prefixes"])
        makerkeys = self._settings.get(["makerkeys"])

        for event in events:
            if event["event_name"] != event_name: continue

            trigger_names = filter(lambda name: name.strip(), event["trigger_names"])

            if not len(trigger_names):
                trigger_names = [prefix + event_name for prefix in default_prefixes]

            value_thunks = [self._interpret_value(event_payload, value) for value in event["values"] + [""] * (3 - len(event["values"]))]
            payload_thunk = lambda: { "value1": value_thunks[0](), "value2": value_thunks[1](), "value3": value_thunks[2]() }

            for trigger_name in trigger_names:
                for makerkey in makerkeys:
                    payload = payload_thunk()
                    url = "https://maker.ifttt.com/trigger/%s/with/key/%s" % (trigger_name, makerkey)
                    self._logger.info("sending a request to url: %s, payload: %s" % (url.replace(makerkey, "[REDACTED; %s...]" % makerkey[:8]), payload));

                    response = requests.post(url, json=payload)
                    self._logger.info("response: " + response.text)

    def _interpret_value(self, payload, value):
        to_thunk = lambda x: lambda: x
        self._logger.info(value)

        if len(value) == 0:
            return to_thunk("")

        if value[0] == ".":
            if value[1:]
                return to_thunk(payload[value[1:]])
            else
                return to_thunk(payload);

        if value[0] == ":":
            return to_thunk(value[1:])

        if value[0] == "@":
            path = self._interpret_value(payload, value[2:])()
            if value[1] == "f":
                path = self._storage_interface.path_on_disk(path)

            return lambda: requests.post("https://file.io", files={ "file": open(path, "rb") }).json()["link"]

        if value[0] == "$":
            if value[1] == "t":
                t = self._interpret_value(payload, value[3:])()
                s = str(int(t)%60)
                m = str(int(t/60)%60)
                h = str(int(t/3600))
                sf = s.zfill(2)
                mf = m.zfill(2)
                hf = h.zfill(2)
                
                if value[2] == "$":
                    return to_thunk('%s:%s:%s' % (hf, mf, sf))
                    
                if value[2] == ":":
                    return to_thunk('%s:%s' % (hf, mf))

                if value[2] == "h":
                    return to_thunk('%sh' % (h))

                if value[2] == "m":
                    return to_thunk('%sh %sm' % (h, m))

                if value[2] == "s":
                    return to_thunk('%sh %sm %ss' % (h, m, s))

                return to_thunk(str(t))

        return to_thunk(value)

    def get_settings_defaults(self):
        return dict(
            makerkeys=[],
            default_prefixes = ["OctoPrint-", "op-"],
            events=[
                dict(event_name="PrintDone", trigger_names=[], values=[".name", ".time", ".origin"]),
                dict(event_name="PrintStarted", trigger_names=[], values=[".name", ".origin", ""]),
                dict(event_name="PrintFailed", trigger_names=[], values=[".name", ".reason", ".origin"]),
            ],
        )

    def get_settings_restricted_paths(self):
        return dict(admin=[["makerkeys"]])

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=True)]

    def get_assets(self):
        return dict(
            js=["js/IFTTT.js"],
            css=["css/IFTTT.css"],
        )

    def get_update_information(self):
        return dict(
            IFTTT=dict(
                displayName="OctoPrint-IFTTT",
                displayVersion=self._plugin_version,

                type="github_release",
                user="tjjfvi",
                repo="OctoPrint-IFTTT",
                current=self._plugin_version,

                pip="https://github.com/tjjfvi/OctoPrint-IFTTT/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "OctoPrint-IFTTT"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = IFTTTplugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
