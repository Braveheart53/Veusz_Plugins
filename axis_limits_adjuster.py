# -*- coding: utf-8 -*-
"""
Axis Limits Adjuster Plugin for Veusz

This plugin allows adjusting X, Y, and Z axis limits for all axes in the document
at once through a single interface.

Author: William W. Wallace
"""

import veusz.plugins.toolsplugin as toolsplugin
import veusz.plugins.field as field

class AxisLimitsAdjuster(toolsplugin.ToolsPlugin):
    """Plugin to adjust X, Y, and Z axis limits for all axes in the document."""

    # Plugin metadata
    menu = ('Axes', 'Adjust All Axis Limits')
    name = 'Adjust All Axis Limits'
    author = 'William W. Wallace'
    description_short = 'Adjust X, Y, and Z axis limits for all axes in the document'
    description_full = ('Allows you to set X, Y, and Z axis limits for all appropriate axes in the document at once. '
                       'If a graph does not have a Z axis, only X and Y limits are applied. '
                       'If an axis is not named X, Y, or Z, it is skipped. '
                       'If the plot type does not have standard X, Y, Z axes, it is skipped.')

    def __init__(self):
        """Initialize the plugin with input fields."""
        self.fields = [
            field.FieldFloatOrAuto(
                'x_min',
                descr='X-axis minimum value (or Auto)',
                default='Auto'
            ),
            field.FieldFloatOrAuto(
                'x_max',
                descr='X-axis maximum value (or Auto)',
                default='Auto'
            ),
            field.FieldFloatOrAuto(
                'y_min',
                descr='Y-axis minimum value (or Auto)',
                default='Auto'
            ),
            field.FieldFloatOrAuto(
                'y_max',
                descr='Y-axis maximum value (or Auto)',
                default='Auto'
            ),
            field.FieldFloatOrAuto(
                'z_min',
                descr='Z-axis minimum value (or Auto)',
                default='Auto'
            ),
            field.FieldFloatOrAuto(
                'z_max',
                descr='Z-axis maximum value (or Auto)',
                default='Auto'
            ),
            field.FieldBool(
                'skip_broken_axes',
                descr='Skip broken axes',
                default=True
            ),
            field.FieldBool(
                'verbose',
                descr='Show detailed output',
                default=False
            )
        ]

    def apply(self, interface, fields):
        """Apply the axis limit adjustments to all appropriate axes."""
        # Get the values from the fields
        x_min = fields['x_min']
        x_max = fields['x_max']
        y_min = fields['y_min']
        y_max = fields['y_max']
        z_min = fields['z_min']
        z_max = fields['z_max']
        skip_broken = fields['skip_broken_axes']
        verbose = fields['verbose']

        # Counter for tracking changes
        axes_modified = 0
        skipped_axes = 0

        # Walk through all widgets in the document
        for widget in interface.Root.WalkWidgets():

            # Only process axis widgets
            if widget.widgettype != 'axis':
                continue

            # Get the axis name (should be something like 'x', 'y', 'z', etc.)
            axis_name = widget.name.lower()

            # Skip broken axes if requested
            if skip_broken and hasattr(widget, 'mode') and widget.mode.val == 'broken':
                if verbose:
                    print(f"Skipping broken axis: {widget.path}")
                skipped_axes += 1
                continue

            # Determine if this is an X, Y, or Z axis based on name or direction
            axis_type = None

            # First check the name directly
            if axis_name in ['x', 'x-axis', 'xaxis']:
                axis_type = 'x'
            elif axis_name in ['y', 'y-axis', 'yaxis']:
                axis_type = 'y'
            elif axis_name in ['z', 'z-axis', 'zaxis']:
                axis_type = 'z'
            else:
                # Check the direction property if name doesn't match
                if hasattr(widget, 'direction'):
                    direction = widget.direction.val.lower()
                    if direction == 'horizontal':
                        axis_type = 'x'
                    elif direction == 'vertical':
                        axis_type = 'y'
                    elif direction in ['depth', 'z']:
                        axis_type = 'z'

            # Skip if we can't determine the axis type
            if axis_type is None:
                if verbose:
                    print(f"Skipping axis with unrecognized type: {widget.path}")
                skipped_axes += 1
                continue

            # Apply the appropriate limits based on axis type
            try:
                if axis_type == 'x':
                    if hasattr(widget, 'min') and x_min != 'Auto':
                        widget.min.val = x_min
                    if hasattr(widget, 'max') and x_max != 'Auto':
                        widget.max.val = x_max
                    if verbose:
                        print(f"Applied X limits to axis: {widget.path}")

                elif axis_type == 'y':
                    if hasattr(widget, 'min') and y_min != 'Auto':
                        widget.min.val = y_min
                    if hasattr(widget, 'max') and y_max != 'Auto':
                        widget.max.val = y_max
                    if verbose:
                        print(f"Applied Y limits to axis: {widget.path}")

                elif axis_type == 'z':
                    if hasattr(widget, 'min') and z_min != 'Auto':
                        widget.min.val = z_min
                    if hasattr(widget, 'max') and z_max != 'Auto':
                        widget.max.val = z_max
                    if verbose:
                        print(f"Applied Z limits to axis: {widget.path}")

                axes_modified += 1

            except Exception as e:
                if verbose:
                    print(f"Error applying limits to axis {widget.path}: {str(e)}")
                raise toolsplugin.ToolsPluginException(
                    f"Error applying limits to axis {widget.path}: {str(e)}"
                )

        # Provide feedback to the user
        message = f"Successfully modified {axes_modified} axes."
        if skipped_axes > 0:
            message += f" Skipped {skipped_axes} axes."

        if axes_modified == 0:
            raise toolsplugin.ToolsPluginException(
                "No axes were found or modified. Check that your document contains "
                "axes named 'x', 'y', or 'z', or axes with horizontal/vertical direction."
            )

        print(message)

# Register the plugin
toolsplugin.toolspluginregistry.append(AxisLimitsAdjuster)
