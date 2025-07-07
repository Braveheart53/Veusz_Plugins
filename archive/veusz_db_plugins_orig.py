
"""
dB Averaging Dataset Plugin for Veusz

This plugin converts dB datasets to linear magnitude, computes their average,
and creates both linear and dB averaged datasets.

Based on the original Veusz_AvgdB.py script.
Author: William W. Wallace
"""
# TODO: dB avg calc is not correct, double check this.....

import numpy as np
# import veusz.plugins as plugins
from veusz.plugins.datasetplugin import (
    DatasetPlugin, DatasetPluginException, Dataset1D, datasetpluginregistry
)
from veusz.plugins import (field)


class dBLinearAvgPlugin(DatasetPlugin):
    """Dataset plugin to average dB datasets in linear domain."""

    # Plugin metadata
    menu = ("Signal Processing", "dB Average")
    name = "dB_Linear_Average"
    author = "William W. Wallace"
    description_short = "Average dB datasets in linear domain"
    description_full = (
        "Converts multiple dB datasets to linear magnitude, "
        "computes their average in linear domain, then provides "
        "both linear magnitude and dB averaged outputs. "
        "This is the correct way to average magnitude data "
        "expressed in dB."
    )

    def __init__(self):
        """Define input fields for the plugin."""
        self.fields = [
            field.FieldDatasetMulti(
                'input_datasets',
                'Input dB datasets'
            ),
            field.FieldText(
                'output_prefix',
                'Output dataset prefix',
                default='avg_'
            ),
            field.FieldText(
                'base_name',
                'Output dataset base name',
                default='avg'
            ),
            field.FieldText(
                'output_suffix',
                'Output dataset suffix',
                default='_avg'
            )
        ]

    def getDatasets(self, fields):
        """Define output datasets."""
        prefix = fields['output_prefix']
        suffix = fields['output_suffix']
        base_name = fields['base_name']
        if not prefix.strip() and not suffix.strip() and not base_name.strip():
            raise DatasetPluginException(
                "Output prefix, base name, AND suffix cannot be empty")

        # Create two output datasets: linear magnitude and dB
        self.linear_output = Dataset1D(
            f"{prefix}{base_name}_linear_mag{suffix}")
        self.db_output = Dataset1D(f"{prefix}{base_name}_dB{suffix}")

        return [self.linear_output, self.db_output]

    def updateDatasets(self, fields, helper):
        """Compute averaged datasets."""
        input_names = fields['input_datasets']

        if not input_names:
            raise DatasetPluginException("No input datasets selected")

        # Get input datasets
        try:
            input_datasets = helper.getDatasets(input_names, dimensions=1)
        except Exception as e:
            raise DatasetPluginException(
                f"Error getting input datasets: {str(e)}")

        if len(input_datasets) == 0:
            raise DatasetPluginException("No valid input datasets found")

        # Convert all dB datasets to linear magnitude
        linear_data = []
        for dataset in input_datasets:
            if dataset.data is None or len(dataset.data) == 0:
                continue

            # Convert dB to linear magnitude: linear = 10^(dB/20)
            linear_mag = 10.0 ** (dataset.data / 20.0)
            linear_data.append(linear_mag)

        if not linear_data:
            raise DatasetPluginException("No valid data to process")

        # Find the maximum length among all datasets
        max_length = max(len(data) for data in linear_data)

        # Pad shorter datasets with NaN to handle different lengths
        # required to create a data_matrix by np.array
        padded_data = []
        for data in linear_data:
            if len(data) < max_length:
                padded = np.full(max_length, np.nan)
                padded[:len(data)] = data
                padded_data.append(padded)
            else:
                padded_data.append(data)

        # Convert to matrix for averaging
        data_matrix = np.array(padded_data)

        # Compute average in linear domain (ignoring NaN values)
        with np.errstate(invalid='ignore', divide='ignore'):
            avg_linear = np.nanmean(data_matrix, axis=0)

        # Convert back to dB: dB = 20*log10(linear)
        with np.errstate(invalid='ignore', divide='ignore'):
            avg_db = 20.0 * np.log10(avg_linear)

        # Handle any infinite or invalid values
        # TODO: Look at placing np.nan...
        avg_linear = np.where(np.isfinite(avg_linear), avg_linear, np.nan)
        avg_db = np.where(np.isfinite(avg_db), avg_db, np.nan)

        # Update output datasets
        self.linear_output.update(data=avg_linear)
        self.db_output.update(data=avg_db)


class dBToLinearPlugin(DatasetPlugin):
    """Dataset plugin to convert dB to linear magnitude."""

    menu = ("Signal Processing", "dB to Linear")
    name = "dB2Linear"
    author = "William W. Wallace"
    description_short = "Convert dB dataset to linear magnitude"
    description_full = (
        "Converts a dB magnitude dataset to linear magnitude "
        "using the formula: linear = 10^(dB/20)"
    )

    def __init__(self):
        """Define input fields."""
        self.fields = [
            field.FieldDataset(
                'input_dataset',
                'Input dB dataset'
            ),
            field.FieldDataset(
                'output_dataset',
                'Output dataset name'
            ),
        ]

    def getDatasets(self, fields):
        """Define output dataset."""
        output_name = fields['output_dataset']
        if not output_name.strip():
            raise DatasetPluginException("Output dataset name cannot be empty")

        self.output = Dataset1D(output_name)
        return [self.output]

    def updateDatasets(self, fields, helper):
        """Convert dB to linear magnitude."""
        input_name = fields['input_dataset']

        try:
            input_dataset = helper.getDataset(input_name, dimensions=1)
        except Exception as e:
            raise DatasetPluginException(f"Error getting input dataset: {str(e)}")

        if input_dataset.data is None or len(input_dataset.data) == 0:
            raise DatasetPluginException("Input dataset is empty")

        # Convert dB to linear magnitude: linear = 10^(dB/20)
        linear_data = 10.0 ** (input_dataset.data / 20.0)

        # Handle error bars if present
        linear_serr = None
        linear_perr = None
        linear_nerr = None

        if input_dataset.serr is not None:
            # For symmetric errors in dB, convert to linear domain
            # Error propagation: if y = 10^(x/20), then dy = y * ln(10)/20 * dx
            conversion_factor = linear_data * np.log(10) / 20.0
            linear_serr = conversion_factor * input_dataset.serr

        if input_dataset.perr is not None:
            conversion_factor = linear_data * np.log(10) / 20.0
            linear_perr = conversion_factor * input_dataset.perr

        if input_dataset.nerr is not None:
            conversion_factor = linear_data * np.log(10) / 20.0
            linear_nerr = conversion_factor * input_dataset.nerr

        self.output.update(
            data=linear_data,
            serr=linear_serr,
            perr=linear_perr,
            nerr=linear_nerr
        )


class LinearTodBPlugin(DatasetPlugin):
    """Dataset plugin to convert linear magnitude to dB."""

    menu = ("Signal Processing", "Linear to dB")
    name = "Linear2dB"
    author = "William W. Wallace"
    description_short = "Convert linear magnitude to dB"
    description_full = (
        "Converts a linear magnitude dataset to dB "
        "using the formula: dB = 20*log10(linear)"
    )

    def __init__(self):
        """Define input fields."""
        self.fields = [
            field.FieldDataset(
                'input_dataset',
                'Input linear dataset'
            ),
            field.FieldDataset(
                'output_dataset',
                'Output dataset name'
            ),
        ]

    def getDatasets(self, fields):
        """Define output dataset."""
        output_name = fields['output_dataset']
        if not output_name.strip():
            raise DatasetPluginException("Output dataset name cannot be empty")

        self.output = Dataset1D(output_name)
        return [self.output]

    def updateDatasets(self, fields, helper):
        """Convert linear magnitude to dB."""
        input_name = fields['input_dataset']

        try:
            input_dataset = helper.getDataset(input_name, dimensions=1)
        except Exception as e:
            raise DatasetPluginException(f"Error getting input dataset: {str(e)}")

        if input_dataset.data is None or len(input_dataset.data) == 0:
            raise DatasetPluginException("Input dataset is empty")

        # Convert linear to dB: dB = 20*log10(linear)
        # Handle zero and negative values
        with np.errstate(invalid='ignore', divide='ignore'):
            db_data = 20.0 * np.log10(np.abs(input_dataset.data))

        # Replace infinite values with a NaN
        db_data = np.where(np.isfinite(db_data), db_data, np.nan)

        # Handle error bars if present
        db_serr = None
        db_perr = None
        db_nerr = None

        # TODO: Test this!
        if input_dataset.serr is not None:
            # Error propagation: if y = 20*log10(x), then dy = 20/(x*ln(10)) * dx
            conversion_factor = 20.0 / (input_dataset.data * np.log(10))
            conversion_factor = np.where(np.isfinite(conversion_factor), conversion_factor, 0.0)
            db_serr = np.abs(conversion_factor * input_dataset.serr)

        if input_dataset.perr is not None:
            conversion_factor = 20.0 / (input_dataset.data * np.log(10))
            conversion_factor = np.where(np.isfinite(conversion_factor), conversion_factor, 0.0)
            db_perr = np.abs(conversion_factor * input_dataset.perr)

        if input_dataset.nerr is not None:
            conversion_factor = 20.0 / (input_dataset.data * np.log(10))
            conversion_factor = np.where(np.isfinite(conversion_factor), conversion_factor, 0.0)
            db_nerr = -np.abs(conversion_factor * input_dataset.nerr)

        self.output.update(
            data=db_data,
            serr=db_serr,
            perr=db_perr,
            nerr=db_nerr
        )


# Register the plugins
# datasetpluginregistry.append([
#     dBLinearAvgPlugin,
#     dBToLinearPlugin,
#     LinearTodBPlugin,
#     ])
datasetpluginregistry.append(dBLinearAvgPlugin)
datasetpluginregistry.append(LinearTodBPlugin)
datasetpluginregistry.append(dBToLinearPlugin)
