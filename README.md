# Veusz_Plugins
Plugins to utilize with Veusz >= 3.6.1

# File/Plugin Description
Each Python script in the root directory is a completed Veusz Plugin.

| File Name | Plugin Function | Completed? | Notes |
| :----: | :----: | :----: | :----: |
| axis_limits_adjuster.py | Adjust all scales or axis on all plots (X,Y,Z) | Y | |
| tag_explorer.py | View all Tags in a Porject | N | Need to test and troubleshoot. |
| touchstone_import_plugin.py | Import of touchstone files directly within Veusz. | N | Currently uses scikit-rf that is not supplied with standalone Veusz. This is due to the use of time domain transforms. Still looking into this. |
| veusz_db_plugins.py | Process data in dB for various transforms. | N | Currently having issues with processing by tag. The menu is Signal Processing, and all functions within this root structure work, the processing by tag is WIP. |

# Work in Progress (WIP)
Currently, all files that a work in progress are copied to the WIP directory. These files will be altered until known working, then replace those in the root directory. Those in the root directory should be working at least to a limited 
expectation.

