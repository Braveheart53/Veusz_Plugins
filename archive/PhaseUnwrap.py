import numpy as np
import veusz.plugins as plugins


class PhaseUnwrapPlugin(plugins.DatasetPlugin):
    """A plugin to unwrap phase datasets in Radians or Degrees."""

    menu = ("Signal Processing","Unwrap Phase")
    name = 'PhaseUnwrap'
    author="William W. Wallace"
    description = 'Unwrap a phase dataset (1D)'

    def __init__(self):
        super(PhaseUnwrapPlugin, self).__init__()
        # Fields for user input in the Veusz dialog
        self.fields = [
            plugins.FieldDataset('dataset', 'Input Dataset'),
            plugins.FieldCombo('units', 'Input Units', ['Radians', 'Degrees'], default='Radians'),
            plugins.FieldText('outname', 'Output Name', default='unwrapped_phase')
        ]

    def getDatasets(self, fields):
        """Perform the unwrapping and return the new dataset."""
        # Get the input data from Veusz
        ds_name = fields['dataset']
        units = fields['units']
        out_name = fields['outname']

        # Read the dataset (handle 1D numeric data)
        data = self.interface.getDataset(ds_name).data

        if units == 'Degrees':
            # Convert to radians, unwrap, then back to degrees
            unwrapped = np.degrees(np.unwrap(np.radians(data)))
        else:
            # Standard radian unwrapping
            unwrapped = np.unwrap(data)

        # Return the new dataset to Veusz
        return [plugins.Dataset1D(out_name, unwrapped)]


# Register the plugin with Veusz
plugins.register(PhaseUnwrapPlugin)
