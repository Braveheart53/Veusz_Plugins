import veusz.plugins as plugins
from veusz.plugins.datasetplugin import (
    DatasetPlugin, DatasetPluginException, Dataset1D, datasetpluginregistry,
    DatasetText
    )
# from veusz.plugins.datasetplugin import DatasetPluginHelper as helper
from veusz.plugins import (field)


class TagExplorerPlugin(DatasetPlugin):
    """Plugin to explore and extract dataset tags."""

    menu = ('Tools', 'Tag Explorer')
    name = 'TagExplorer'
    description_short = 'Explore dataset tags and attributes'
    description_full = 'Comprehensive plugin to explore dataset tags and metadata'

    def __init__(self):
        """Initialize plugin fields."""
        self.fields = [
            plugins.FieldDataset('input_dataset', 'Input Dataset'),
            plugins.FieldDataset('tags_output', 'Tags Output Dataset'),
            plugins.FieldDataset('info_output', 'Info Output Dataset'),
        ]

    def getDatasets(self, fields):
        """Get output datasets."""
        self.tags_ds = plugins.DatasetText(fields['tags_output'])
        self.info_ds = plugins.DatasetText(fields['info_output'])
        return [self.tags_ds, self.info_ds]

    def updateDatasets(self, fields, helper):
        """Update datasets with tag and attribute information."""
        dataset_name = fields['input_dataset']

        try:
            # Access document data through helper._doc
            document_data = helper._doc.data

            if dataset_name in document_data:
                dataset = document_data[dataset_name]

                # Extract tags
                tags = []
                if hasattr(dataset, 'tags'):
                    tags = list(dataset.tags) if dataset.tags else []

                # Extract general dataset information
                info = []
                info.append(f"Dataset: {dataset_name}")
                info.append(f"Type: {type(dataset).__name__}")
                info.append(f"Dimensions: {getattr(dataset, 'dimensions', 'Unknown')}")
                info.append(f"Data type: {getattr(dataset, 'datatype', 'Unknown')}")

                # List all attributes for debugging
                attributes = [attr for attr in dir(dataset) if not attr.startswith('_')]
                info.append(f"Attributes: {', '.join(attributes)}")

                # Update outputs
                self.tags_ds.update(data=tags if tags else ['No tags'])
                self.info_ds.update(data=info)

            else:
                self.tags_ds.update(data=['Dataset not found'])
                self.info_ds.update(data=['Dataset not found'])

        except Exception as e:
            error_msg = f'Error accessing dataset: {str(e)}'
            self.tags_ds.update(data=[error_msg])
            self.info_ds.update(data=[error_msg])

# Register the plugin
datasetpluginregistry.append(TagExplorerPlugin())
