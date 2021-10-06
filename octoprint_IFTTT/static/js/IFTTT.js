$(function() {
    function IFTTTviewModel(parameters) {
        let self = this, root = self;

		self.startupComplete = ko.observable(false);

		self.makerkeys = ko.computed({
			read: () => self.startupComplete() && self.settings.makerkeys().join("\n"),
			write: mks => self.startupComplete() && self.settings.makerkeys(mks.split("\n")),
		});

		self.webhook = ko.computed({
			read: () => self.startupComplete() && self.settings.webhook(),
			write: mks => self.startupComplete() && self.settings.webhook(mks),
		});

		self.defaultPrefixes = ko.computed({
			read: () => self.startupComplete() && self.settings.default_prefixes().join("\n"),
			write: dps => self.startupComplete() && self.settings.default_prefixes(dps.split("\n")),
		});

		self.events = ko.computed(() =>
			self.startupComplete() ? self.settings.events() : []
		);

		self.newEvent = () =>
			self.settings.events.push({
				event_name: ko.observable(''),
				trigger_names: ko.observable([]),
				values: ko.observable([])
			})

		self.onStartupComplete = () => {
			self.settings = parameters[0].settings.plugins.IFTTT;
			self.startupComplete(true);
			// console.log(self.settings.events(), self.events());
		}

		self.Event = function(event){
			let self = this;

			self.name = event.event_name;
			self.placeholder = ko.computed(() => {
				console.log(root.settings.default_prefixes(), event);
				return root.startupComplete() ?
					root.settings.default_prefixes().map(prefix => prefix + self.name()).join("\n") :
					""
			});
			self.triggerNames = ko.computed({
				read: () => root.startupComplete() && event.trigger_names().join("\n"),
				write: mks => root.startupComplete() && event.trigger_names(mks.split("\n")),
			});
			console.log(event);
			[...[,,,]].map((_, i) => self["value" + (i+1)] = ko.computed({
				read: () => event.values()[i],
				write: val => event.values(Object.assign(event.values().slice(), { [i]: val })),
			}));
			self.remove = () => root.settings.events.remove(event);
		}
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: IFTTTviewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_IFTTT"],
    });
});
