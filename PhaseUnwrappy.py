# -*- coding: utf-8 -*-
"""
Phase Unwrap Dataset Plugin for Veusz.

This plugin unwraps phase datasets that contain discontinuities,
converting wrapped phase values to a continuous unwrapped phase curve.
Supports both radians and degrees.

Based on NumPy's np.unwrap() algorithm.

Author: William W. Wallace
"""

# %% Module Import

import numpy as np

from veusz.plugins.datasetplugin import (
    DatasetPlugin,
    DatasetPluginException,
    Dataset1D,
    datasetpluginregistry,
)

from veusz.plugins import field

# %% Class Definitions


class PhaseUnwrapPlugin(DatasetPlugin):
    """Dataset plugin to unwrap phase datasets."""

    # Plugin metadata
    menu = ("Signal Processing", "Unwrap Phase")
    name = "PhaseUnwrap"
    author = "William W. Wallace"
    description_short = "Unwrap a phase dataset (1D)"
    description_full = (
        "Unwraps a phase dataset by detecting and removing "
        "discontinuities larger than π radians (180 degrees). "
        "Supports both radian and degree inputs. "
        "Based on NumPy's unwrap algorithm."
    )

    def __init__(self):
        """Define input fields for the plugin."""
        self.fields = [
            field.FieldDataset(
                "input_dataset",
                "Input phase dataset",
            ),
            field.FieldCombo(
                "units",
                "Input units",
                items=["Radians", "Degrees"],
                default="Radians",
            ),
            field.FieldText(
                "output_dataset",
                "Output dataset name",
                default="unwrapped_phase",
            ),
        ]

    def getDatasets(self, fields):
        """Define output dataset.

        Returns:
            list: List containing the output Dataset1D object.
        """
        output_name = fields["output_dataset"]

        if not output_name.strip():
            raise DatasetPluginException("Output dataset name cannot be empty")

        self.output = Dataset1D(output_name)
        return [self.output]

    def updateDatasets(self, fields, helper):
        """Compute unwrapped phase dataset.

        Detects phase discontinuities larger than π radians and adds/subtracts
        multiples of 2π (or 360 degrees) to create a continuous unwrapped phase.

        Args:
            fields (dict): User input fields containing input_dataset, units, output_dataset.
            helper (DatasetPluginHelper): Helper object for accessing datasets.

        Raises:
            DatasetPluginException: If input dataset is invalid or empty.
        """
        input_name = fields["input_dataset"]
        units = fields["units"]

        try:
            input_dataset = helper.getDataset(input_name, dimensions=1)
        except Exception as e:
            raise DatasetPluginException(
                f"Error getting input dataset: {str(e)}"
            )

        if input_dataset.data is None or len(input_dataset.data) == 0:
            raise DatasetPluginException("Input dataset is empty")

        # Unwrap phase based on input units
        if units == "Degrees":
            # Convert degrees to radians, unwrap, convert back to degrees
            # Phase unwrap operates on radians (2π discontinuity)
            # Mathematical equivalence:
            #   unwrap(deg) = unwrap(rad * 180/π) * π/180
            unwrapped = np.degrees(np.unwrap(np.radians(input_dataset.data)))
        else:
            # Standard radian unwrapping (2π discontinuity detection)
            unwrapped = np.unwrap(input_dataset.data)

        # Handle error bars if present (error bars don't change with unwrapping)
        unwrapped_serr = None
        unwrapped_perr = None
        unwrapped_nerr = None

        if input_dataset.serr is not None:
            unwrapped_serr = input_dataset.serr

        if input_dataset.perr is not None:
            unwrapped_perr = input_dataset.perr

        if input_dataset.nerr is not None:
            unwrapped_nerr = input_dataset.nerr

        # Update output dataset
        self.output.update(
            data=unwrapped,
            serr=unwrapped_serr,
            perr=unwrapped_perr,
            nerr=unwrapped_nerr,
        )


# %% Register Plugin

datasetpluginregistry.append(PhaseUnwrapPlugin)
