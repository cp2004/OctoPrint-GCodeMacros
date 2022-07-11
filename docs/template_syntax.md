# Macro Template Syntax

The Gcode Macros plugin uses Jinja2 to render each macro adding some extra features.

## Including external files in macros

If you have a very long macro, you will want to include it as an external file. Massive macros can slow down loading the UI,
and make OctoPrint's config.yaml file very large as well.

The plugin looks for files in its data folder. On an OctoPi install, this would be `~/.octoprint/data/gcode_macro/`. On other platforms
the structure is the same, `'OctoPrint's data folder'/data/gcode_macro`.

For example, you may create a file such as `bed_level_test.gcode` in the data folder. To reference it in a macro, use it like this:

```jinja
{% include "bed_level_test.gcode" %}

```

You will have to create and manage these files manually for now.

Any questions, please get in touch. If you would like to improve the documentation, please open a PR.
