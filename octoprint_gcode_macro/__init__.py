import os
from pathlib import Path

import octoprint.plugin
from jinja2 import Environment, FileSystemLoader

from octoprint_gcode_macro import _version

__version__ = _version.get_versions()["version"]
del _version


# These macros will be ignored, because they are known to be already taken
FORBIDDEN_MACROS = [
    "cancel",
    "abort",
    "pause",
    "resume",
]
DESCRIPTION_START_MARKER = "START_DESCRIPTION"
DESCRIPTION_END_MARKER = "END_DESCRIPTION"


class GcodeMacroPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
):
    def __init__(self):
        super().__init__()
        self.macros = {}
        # Structure:
        # {
        #     "a command": {
        #         "content": "Some example content",
        #         "description": "A description of the macro",
        #     }
        # }

        self.jinja_env: Environment

    # SettingsPlugin mixin
    def get_settings_defaults(self):
        # TODO a default macro
        return {
            "macros": [
                {
                    "command": "example",
                    "content": "M117 Hello!",
                    "description": "An example macro you can customize",
                }
            ]
        }

    def get_settings_version(self):
        return 1

    def on_settings_migrate(self, target, current):
        if current is None or current < 1:
            # Shift settings from config.yaml to files in plugin data folder
            current_macros = self._settings.get(["macros"], merged=True)
            # Process into the correct structure
            result = {}
            for macro in current_macros:
                result[macro["command"]] = {
                    "content": macro["content"],
                    "description": macro["description"],
                }
            self.save_macros(result)
            self._settings.remove(["macros"])

    def initialize(self):
        # Data folder is not available until now
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.get_plugin_data_folder()),
        )
        self.reload_macros()

    def on_settings_save(self, data):
        # Extract macros, so they don't end up in config.yaml
        macros = data.pop("macros")
        self.save_macros(macros)
        # If we have any other settings, save them now
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

    def load_macros(self):
        """
        Macros are stored as files in the plugin data folder (+ /macros) and are loaded into memory & available on the
        settings API to edit.
        """
        macro_path = os.path.join(self.get_plugin_data_folder(), "macros")

        # We don't support folders here, just files. They have the extension .gcode, filename is the command
        # TODO check the limitations on filenames vs. macro names
        # An alternative would be to store the name in the first line of the file or something
        # TODO some kind of validation on anything?

        for file in Path(macro_path).glob("*.gcode"):
            command = os.path.splitext(file.name)[0]
            description = ""
            content = ""
            with file.open("r") as f:
                reading_description = False
                for line in f:
                    if line.strip() == DESCRIPTION_START_MARKER:
                        reading_description = True
                    elif line.strip() == DESCRIPTION_END_MARKER:
                        reading_description = False
                    else:
                        if reading_description:
                            description += line
                        else:
                            content += line

            description.rstrip()  # Remove any whitespace from the end of description

            self._logger.info(f"Macro loaded :@{command}, {description}")

            self.macros[command] = content

    def save_macros(self, macros):
        """
        Save macros to the plugin data folder

        File format:
        name: <command>.gcode

        START_DESCRIPTION
        <description>
        END_DESCRIPTION

        """
        macro_path = os.path.join(self.get_plugin_data_folder(), "macros")
        if not os.path.isdir(macro_path):
            # Make the `macros` folder if it doesn't exist
            os.makedirs(macro_path)

        for macro in macros:
            command = macro["command"]
            content = macro["content"]
            description = macro["description"]

            self.macros[command] = {
                "content": content,
                "description": description,
            }

            if command in FORBIDDEN_MACROS:
                self._logger.warning(
                    f"Forbidden macro command was attempted to be saved ({command})"
                )
                continue

            # TODO
            # if content == self.macros[command] and description == self.macros:
            #     # No change, no need to save
            #     continue

            file = os.path.join(macro_path, f"{command}.gcode")
            with open(file, "wt") as f:
                f.write(f"{DESCRIPTION_START_MARKER}\n")
                f.write(description)
                f.write(f"\n{DESCRIPTION_END_MARKER}\n")
                f.write(content)

    # AssetPlugin mixin
    def get_assets(self):
        return {
            "js": ["gcode_macro.js"],
            "css": ["dist/gcode_macro.css"],
        }

    def gcode_queueing(
        self,
        c,
        p,
        command,
        ct,
        g,
        subcode=None,
        tags=None,
        *args,
        **kwargs,
    ):
        if command.startswith("@"):
            return self.render_macro(command)

    def render_macro(self, command, level=0):
        """
        Render a macro from a command
        :param command: string, macro to lookup
        :param level: int, number of sub-macros that have been rendered
        :return: list, list of commands to send to the printer
        """
        command = command.strip("@")

        if command in FORBIDDEN_MACROS or command not in self.macros.keys():
            # Forbidden, illegal, not a macro command, ignore, leave command unchanged.
            return

        self._logger.debug(f"Rendering macro for @ command @{command}")

        content = self.render_with_jinja(command)

        if content and isinstance(content, str):
            # Split long string into list of commands for OctoPrint to digest
            commands = content.split("\n")
            # Strip gcode comments & whitespace
            commands = list(map(lambda x: x.split(";")[0].strip(), commands))

            result = []

            if level <= 4:
                # Only render up to 5 levels (0 start)
                # Seems like a sane limit, don't want crashes from circular macros
                for cmd in commands:
                    if cmd.startswith("@"):
                        # Recursively render for each @ command in macro
                        result += self.render_macro(cmd, level=level + 1)
                    else:
                        result += [cmd]
            else:
                self._logger.warning(
                    f"Recursive limit hit trying to render macro {command}"
                )

            return result

        # If in doubt, just return nothing so the command remains unchanged.
        return

    def get_macro_content(self, command):
        try:
            content = self.macros[command]
        except KeyError as e:
            # In theory this shouldn't happen with the check above, but if it does, I want to know
            self._logger.exception(e)
            content = []

        return content

    def render_with_jinja(self, command):
        content = self.get_macro_content(command)

        try:
            template = self.jinja_env.from_string(content)
            return template.render()
        except Exception as e:
            self._plugin_manager.send_plugin_message(
                "gcode_macro", {"type": "rendering_error", "command": command}
            )
            self._logger.error(f"Error while rendering macro for {command}")
            self._logger.exception(e)
            return ""

    # Software update hook
    def get_update_information(self):
        return {
            "gcode_macro": {
                "displayName": "Gcode Macros",
                "displayVersion": self._plugin_version,
                # version check: github repository
                "type": "github_release",
                "user": "cp2004",
                "repo": "OctoPrint-GcodeMacros",
                "current": self._plugin_version,
                "stable_branch": {
                    "name": "Stable",
                    "branch": "master",
                    "comittish": ["master"],
                },
                "prerelease_branches": [
                    {
                        "name": "Release Candidate",
                        "branch": "pre-release",
                        "comittish": ["pre-release", "master"],
                    }
                ],
                # update method: pip
                "pip": "https://github.com/cp2004/OctoPrint-GcodeMacros/releases/download/{target_version}/release.zip",
            }
        }


__plugin_name__ = "Gcode Macros"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_version__ = __version__


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = GcodeMacroPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.gcode_queueing,
    }
