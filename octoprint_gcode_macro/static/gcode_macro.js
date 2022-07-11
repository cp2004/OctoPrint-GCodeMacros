/*
 * View model for Gcode Macros
 *
 * Author: Charlie Powell
 * License: AGPLv3
 */

$(function () {
  function gcodeMacroViewModel(parameters) {
    const self = this;
    self.settings = parameters[0];

    // Keep in sync with python list
    self.FORBIDDEN_MACROS = ["cancel", "abort", "pause", "resume"];

    self.selectedMacro = ko.observable({
      command: "",
      content: "",
      description: "",
    });
    self.newMacroName = ko.observable("");

    self.allMacroNames = () => {
      if (self.settings.settings) {
        // Settings are not defined on binding, only after settings fetch
        return self.settings.settings.plugins.gcode_macro
          .macros()
          .map((macro) => macro.command);
      } else {
        return [];
      }
    };

    self.createMacro = () => {
      if (self.isMacroTaken(self.newMacroName())) {
        // Name is already taken, refuse to create - button should already be disabled
        return;
      }
      self.selectedMacro({
        command: ko.observable(self.newMacroName()),
        content: ko.observable(""),
        description: ko.observable(""),
      });
      self.settings.settings.plugins.gcode_macro.macros.push(
        self.selectedMacro()
      );
      $("#gcodeMacroEditor").modal("show");
      self.newMacroName("");
    };

    self.editMacro = (data) => {
      self.selectedMacro(data);
      $("#gcodeMacroEditor").modal("show");
    };

    self.deleteMacro = (data) => {
      self.settings.settings.plugins.gcode_macro.macros.remove(data);
    };

    self.isMacroTaken = (name) =>
      self.FORBIDDEN_MACROS.includes(name) ||
      self.allMacroNames().includes(name);

    self.newMacroValid = ko.computed(() => {
      const macros = self
        .allMacroNames()
        .map((name) => name())
        .concat(self.FORBIDDEN_MACROS);
      return !macros.includes(self.newMacroName());
    });

    self.onDataUpdaterPluginMessage = function (plugin, data) {
      if (plugin !== "gcode_macro") return;
      if (data.type === "rendering_error") {
        new PNotify({
          title: "Error rendering macro <code>@" + data.command + "</code>",
          text:
            "There was an error rendering the macro. Please check your macro content and try again. " +
            "For more details check the <code>octoprint.log</code>.",
          type: "error",
          hide: false,
        });
      }
    };
  }

  OCTOPRINT_VIEWMODELS.push({
    construct: gcodeMacroViewModel,
    name: "GcodeMacroViewModel",
    dependencies: ["settingsViewModel"],
    elements: ["#settings_plugin_gcode_macro"],
  });
});
