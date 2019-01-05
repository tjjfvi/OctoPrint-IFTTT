# coding=utf-8
from __future__ import absolute_import

import octoprint
import requests
#from datauri import DataURI

class IFTTTplugin(
	octoprint.plugin.StartupPlugin,
	octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
	octoprint.plugin.EventHandlerPlugin,
):
	def on_after_startup(self):
		self._storage_interface = self._file_manager._storage("local")

	def on_event(self, event_name, payload):
		events = self._settings.get(["events"])
		default_prefixes = self._settings.get(["default_prefixes"])
		makerkeys = self._settings.get(["makerkeys"])


		for event in events:
			if event["event_name"] != event_name: continue

			trigger_names = event["trigger_names"]

			if not len(trigger_names):
				trigger_names = [prefix + event_name for prefix in default_prefixes]

			values = [self._interpret_value(payload, value) for value in event["values"]]
			payload = { "value1": values[0], "value2": values[1], "value3": values[2] }

			for trigger_name in trigger_names:
				for makerkey in makerkeys:
					url = "https://maker.ifttt.com/trigger/%s/with/key/%s" % (trigger_name, makerkey)
					self._logger.info("sending a request to url: %s, payload: %s" % (url.replace(makerkey, "[REDACTED; %s...]" % makerkey[:8]), payload));

					response = requests.post(url, json=payload)
					self._logger.info("response: " + response.text)

	def _interpret_value(self, payload, value):
		self._logger.info(value)
		if len(value) == 0:
			return ""
		if value[0] == ".":
			return payload[value[1:]]
		if value[0] == ":":
			return value[1:]
		#if value[0] == "@":
			#path = self._interpret_value(payload, value[(2 if value[1] in "-f" else 1):])
			#if value[1] == "f":
			#	path = self._storage_interface.path_on_disk(path)
			#return DataURI.from_file(path)
		return value

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
