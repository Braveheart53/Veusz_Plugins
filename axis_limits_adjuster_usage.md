# Veusz Axis Limits Adjuster Plugin - Usage Guide

## Installation

1. **Save the plugin file**: Save the `axis_limits_adjuster.py` file to your computer.

2. **Install in Veusz**:
   - Open Veusz
   - Go to Edit → Preferences
   - Click on the "Plugins" tab
   - Click "Add..." button
   - Navigate to and select the `axis_limits_adjuster.py` file
   - Click "OK" to close preferences
   - Restart Veusz for the plugin to be available

## Usage

1. **Access the plugin**:
   - Once installed, the plugin will appear in the menu: **Data → Axes → Adjust All Axis Limits**

2. **Plugin interface fields**:
   - **X-min**: Minimum value for X-axes (enter number or leave as "Auto")
   - **X-max**: Maximum value for X-axes (enter number or leave as "Auto") 
   - **Y-min**: Minimum value for Y-axes (enter number or leave as "Auto")
   - **Y-max**: Maximum value for Y-axes (enter number or leave as "Auto")
   - **Z-min**: Minimum value for Z-axes (enter number or leave as "Auto")
   - **Z-max**: Maximum value for Z-axes (enter number or leave as "Auto")
   - **Skip broken axes**: Check to skip axes with "broken" mode
   - **Show detailed output**: Check to see verbose information about which axes were modified

3. **How it works**:
   - The plugin scans ALL axis widgets in the entire document
   - It identifies X, Y, and Z axes by:
     - Name matching: 'x', 'x-axis', 'xaxis', 'y', 'y-axis', 'yaxis', 'z', 'z-axis', 'zaxis'
     - Direction property: 'horizontal' → X-axis, 'vertical' → Y-axis, 'depth'/'z' → Z-axis
   - Applies the specified limits only to matching axes
   - Skips axes that don't match X, Y, or Z criteria
   - Leaves "Auto" values unchanged

## Examples

### Example 1: Set all X-axes to range 0-10, all Y-axes to range -5 to 5
- X-min: 0
- X-max: 10
- Y-min: -5
- Y-max: 5
- Z-min: Auto (unchanged)
- Z-max: Auto (unchanged)

### Example 2: Set only minimum values, leave maximums automatic
- X-min: 0
- X-max: Auto
- Y-min: 0
- Y-max: Auto
- Z-min: Auto
- Z-max: Auto

### Example 3: Set all axes to the same range
- X-min: -100
- X-max: 100
- Y-min: -100
- Y-max: 100
- Z-min: -100
- Z-max: 100

## Troubleshooting

**Problem**: "No axes were found or modified" error
**Solution**: 
- Check that your document contains graphs with axis widgets
- Verify axis names match expected patterns (x, y, z) or have proper direction settings
- Enable "Show detailed output" to see which axes are being skipped

**Problem**: Plugin doesn't appear in menu
**Solution**:
- Ensure you restarted Veusz after adding the plugin
- Check the plugin file is correctly placed and accessible
- Look for any error messages in the Veusz console

**Problem**: Some axes aren't being modified
**Solution**:
- Check if they are broken axes (enable "Skip broken axes" or disable it)
- Verify the axis names - custom named axes might not be recognized
- Enable verbose output to see exactly which axes are being processed

## Technical Details

The plugin uses the Veusz Tools Plugin framework and:
- Inherits from `toolsplugin.ToolsPlugin`
- Uses `field.FieldFloatOrAuto` for numeric input with "Auto" option
- Uses `field.FieldBool` for checkbox options
- Walks through all widgets using `interface.Root.WalkWidgets()`
- Filters for `widget.widgettype == 'axis'`
- Modifies `widget.min.val` and `widget.max.val` properties
- Provides error handling with `toolsplugin.ToolsPluginException`
