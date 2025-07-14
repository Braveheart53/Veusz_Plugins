# -*- coding: utf-8 -*-
"""
Veusz Mean Center Range Plugin
A dataset plugin that applies mean-centering range
calculation to multiple datasets.

Author: William W. Wallace
"""

import numpy as np -- numpy already imported as *
import veusz.plugins as plugins
import veusz.plugins.field as field

class MeanCenterRangePlugin(plugins.DatasetPlugin):
    """Dataset plugin to create mean-centered ranges for multiple datasets."""

    # Plugin menu location
    menu = ('Signal Processing', 'Mean Center Range')

    # Plugin name for internal use
    name = 'MeanCenterRange'

    # Plugin descriptions
    description_short = 'Create mean-centered ranges for multiple datasets'
    description_full = ('Create mean-centered ranges for multiple datasets using the formula:\n'
                       'offset = mean(data) - reference_frequency\n'
                       'dataMin = -ptp(data)/2 + offset\n'
                       'dataMax = ptp(data)/2 + offset\n'
                       'newRange = linspace(dataMin, dataMax, num_points)')

    def __init__(self):
        """Define input fields for plugin."""
        self.fields = [
            plugins.FieldDatasetMulti('input_datasets', 'Input datasets'),
            plugins.FieldFloat('reference_freq', 'Reference frequency',
                               default=10e6),
            plugins.FieldInt('num_points', 'Number of points', default=801),
            plugins.FieldText('output_suffix', 'Output suffix',
                              default='_meanCentered'),
        ]

        # Will store output datasets
        self.output_datasets = []

    def getDatasets(self, fields):
        """Create output datasets based on input field values."""

        # Validate input datasets
        input_datasets = fields['input_datasets']
        if not input_datasets:
            raise plugins.DatasetPluginException('No input datasets specified')

        # Clear previous output datasets
        self.output_datasets = []

        # Create output dataset for each input dataset
        for dataset_name in input_datasets:
            if dataset_name.strip():
                output_name = dataset_name.strip() + fields['output_suffix']
                output_dataset = plugins.Dataset1D(output_name)
                self.output_datasets.append(output_dataset)

        if not self.output_datasets:
            raise plugins.DatasetPluginException(
                'No valid input datasets found')

        return self.output_datasets

    def updateDatasets(self, fields, helper):
        """Update output datasets with mean-centered range data."""
        # Get parameters
        input_datasets = fields['input_datasets']
        reference_freq = fields['reference_freq']
        num_points = fields['num_points']

        # Process each input dataset
        for i, dataset_name in enumerate(input_datasets):
            if not dataset_name.strip():
                continue

            try:
                # Get input dataset
                input_dataset = helper.getDataset(dataset_name.strip())
                data = input_dataset.data

                # Check if data is valid
                if len(data) == 0:
                    raise plugins.DatasetPluginException(
                        f'Dataset "{dataset_name}" is empty')

                # Calculate offset: mean(data) - reference_freq
                offset = np.mean(data) - reference_freq

                # Calculate min and max using peak-to-peak
                ptp_value = np.ptp(data)  # peak-to-peak
                data_min = -ptp_value / 2 + offset
                data_max = ptp_value / 2 + offset

                # Create the new range using linspace
                new_range = np.linspace(data_min, data_max, num_points)

                # Update the corresponding output dataset
                if i < len(self.output_datasets):
                    self.output_datasets[i].update(data=new_range)

            except Exception as e:
                # Handle errors for individual datasets
                if i < len(self.output_datasets):
                    # Set empty data for failed datasets
                    self.output_datasets[i].update(data=array([]))

                # Log error but continue processing other datasets
                raise plugins.DatasetPluginException(
                    f'Error processing dataset "{dataset_name}": {str(e)}')


# Single dataset version for simpler use cases
class MeanCenterRangeSinglePlugin(plugins.DatasetPlugin):
    """Dataset plugin to create mean-centered range for a single dataset."""

    # Plugin menu location
    menu = ('Signal Processing', 'Mean Center Range (Single)')

    # Plugin name for internal use
    name = 'MeanCenterRangeSingle'
    author = 'William W. Wallace'

    # Plugin descriptions
    description_short = 'Create mean-centered range for a single dataset'
    description_full = ('Create mean-centered range for a single dataset using the formula:\n'
                       'offset = mean(data) - reference_frequency\n'
                       'dataMin = -ptp(data)/2 + offset\n'
                       'dataMax = ptp(data)/2 + offset\n'
                       'newRange = linspace(dataMin, dataMax, num_points)')

    def __init__(self):
        """Define input fields for plugin."""
        self.fields = [
            plugins.FieldDataset('input_dataset', 'Input dataset'),
            plugins.FieldFloat('reference_freq', 'Reference frequency', default=10e6),
            plugins.FieldInt('num_points', 'Number of points', default=801),
            plugins.FieldDataset('output_dataset', 'Output dataset name'),
        ]

        # Will store output dataset
        self.output_dataset = None

    def getDatasets(self, fields):
        """Create output dataset based on input field values."""

        # Validate output dataset name
        output_name = fields['output_dataset']
        if not output_name.strip():
            raise plugins.DatasetPluginException('Invalid output dataset name')

        # Create output dataset
        self.output_dataset = plugins.Dataset1D(output_name)

        return [self.output_dataset]

    def updateDatasets(self, fields, helper):
        """Update output dataset with mean-centered range data."""

        # Get parameters
        input_dataset_name = fields['input_dataset']
        reference_freq = fields['reference_freq']
        num_points = fields['num_points']

        try:
            # Get input dataset
            input_dataset = helper.getDataset(input_dataset_name)
            data = input_dataset.data

            # Check if data is valid
            if len(data) == 0:
                raise plugins.DatasetPluginException(
                    f'Dataset "{input_dataset_name}" is empty')

            # Calculate offset: mean(data) - reference_freq
            offset = np.mean(data) - reference_freq

            # Calculate min and max using peak-to-peak
            ptp_value = np.ptp(data)  # peak-to-peak
            data_min = -ptp_value / 2 + offset
            data_max = ptp_value / 2 + offset

            # Create the new range using linspace
            new_range = np.linspace(data_min, data_max, num_points)

            # Update the output dataset
            self.output_dataset.update(data=new_range)

        except Exception as e:
            # Handle errors
            self.output_dataset.update(data=array([]))
            raise plugins.DatasetPluginException(
                f'Error processing dataset "{input_dataset_name}": {str(e)}')


# Register the plugins
plugins.datasetpluginregistry.append(MeanCenterRangePlugin)
plugins.datasetpluginregistry.append(MeanCenterRangeSinglePlugin)
