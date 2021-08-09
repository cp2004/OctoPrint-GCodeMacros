/*
 * View model for Gcode Macros
 *
 * Author: Charlie Powell
 * License: AGPLv3
 */

const ko = window.ko
const $ = window.$
const OCTOPRINT_VIEWMODELS = window.OCTORPINT_VIEWMODELS

$(function () {
  function gcodeMacroViewModel (parameters) {
    const self = this
    self.settings = parameters[0]

    // Keep in sync with python list
    self.FORBIDDEN_MACROS = [
      'cancel',
      'abort',
      'pause',
      'resume'
    ]

    self.selectedMacro = ko.observable()
    self.newMacroName = ko.observable('')

    self.createMacro = () => {
      self.selectedMacro({
        command: ko.observable(self.newMacroName()),
        content: ko.observable(''),
        description: ko.observable('')
      })
      self.settings.settings.plugins.gcode_macro.macros.push(self.selectedMacro())
      $('#gcodeMacroEditor').modal('show')
      self.newMacroName('')
    }

    self.editMacro = (data) => {
      self.selectedMacro(data)
      $('#gcodeMacroEditor').modal('show')
    }

    self.deleteMacro = (data) => {
      self.settings.settings.plugins.gcode_macro.macros.remove(data)
    }
  }
  OCTOPRINT_VIEWMODELS.push({
    construct: gcodeMacroViewModel,
    name: 'GcodeMacroViewModel',
    dependencies: ['settingsViewModel'],
    elements: ['#settings_plugin_gcode_macro']
  })
})
