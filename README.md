# OctoPrint Gcode Macros Plugin

Create custom commands you can add anywhere: in your gcode file, OctoPrint's terminal, gcode scripts, or other plugins
to run a configured script.

Use macros for preheating your printer, levelling the bed, changing filament... Possibilities are (nearly) endless!

## Installation

Install from the [plugin repository](https://plugins.octoprint.org/plugins/gcode_macro) or manually using this URL:

    https://github.com/cp2004/OctoPrint-GCodeMacros/releases/latest/download/release.zip

**Warning:** This plugin only supports Python 3 installs. To find out more about upgrading your OctoPrint install to
Python 3, you can take a look
[at this post](https://community.octoprint.org/t/upgrading-your-octoprint-install-to-python-3/35158?u=charlie_powell)

**Warning 2:** Don't try installing this plugin from the source code on GitHub, since it has a build step for
the frontend code. If you are interested in contributing, please see [the Contribution Guidelines](CONTRIBUTING.md)

## Configuration

Once installed, you can start defining your macros.

### Macro Commands

All commands are prefixed with an `@`, so they don't interfere with standard gcode commands. However, this means that
**some commands are reserved**. OctoPrint uses
[these specific commands](https://docs.octoprint.org/en/master/features/atcommands.html) for pausing & resuming prints,
but also other plugins can use custom @ commands. For example, OctoLapse uses `@OCTOLAPSE TAKE-SNAPSHOT` or the WLED
plugin uses `@WLED ON` or `@WLED OFF` to control some LEDs.

The commands are **case sensitive**, and you can have spaces, numbers and punctuation in them!

*These commands will not work while printing from the printer's SD card*

### Macro Content

Macros can contain anything, even other macros!

You can nest macros up to 5 levels deep. For example, you may have a macro `@preheat`, and one for `@bedlevel`. Maybe
you want to preheat your bed before running the levelling commands!

In addition to nesting commands, you can also use the Jinja2 template syntax to implement some logic in scripts.
For example, this one will make the printer move to a random position in X and Y:

`@random`

```
G1 X{{ range(200) | random}} Y{{ range(200) | random }} F3000.0;
```

Or maybe you fancy having a bit of fun, making your printer into a random number generator:

`@random-number`

```
M117 Random number... {{ range(100) | random }}!
```

**See the full [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/2.11.x/templates/#random)
for more information about the templates**

## Sponsors

* [@iFrostizz](https://github.com/iFrostizz)
* [@KenLucke](https://github.com/KenLucke)

As well as 7 others supporting me through [GitHub Sponsors](https://github.com/sponsors/cp2004)!

## Supporting my efforts

I created this project in my spare time, so if you have found it useful or enjoyed using it then please consider [supporting it's development!](https://github.com/sponsors/cp2004). You can sponsor monthly or one time, for any amount you choose.
## 👷
