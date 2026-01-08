"""
RPi TKu Telemetry File Import Plugin for Veusz 4.2 - ENHANCED VERSION (FIXED)

This plugin imports RPi TKu telemetry data files (.dat) and automatically:
- Creates datasets for each column with appropriate naming
- Tags voltage datasets (ending in 'V') with "Voltages"
- Tags amperage datasets (ending in 'A') with "Amperages"
- Tags state/detector datasets (starting with 'Det') with "StateValues"
- Tags datetime columns with "DateTime"
- Converts MJD timestamps to readable YYYY-MM-DD HH:MM:SS format
- Stores metadata for post-processing plot generation
- Includes all header information in dataset properties

This enhanced version provides better metadata organization for subsequent
plot generation either through companion plugins or manual processes.

Created by: William W. Wallace
Modified for: RPi TKu telemetry files
Version: 1.1 (Enhanced) - FIXED
"""

import os
import numpy as np
from datetime import datetime, timedelta

# Import the necessary Veusz plugin components
from veusz.plugins.importplugin import (
    ImportPlugin, ImportPluginParams, ImportPluginException,
    importpluginregistry
)

from veusz.plugins import (
    field, ImportDataset1D, ImportDatasetText
)


class RPiTKuImportPluginEnhanced(ImportPlugin):
    """
    Enhanced import plugin for RPi TKu telemetry files (.dat).
    
    This version provides comprehensive metadata tracking and support for
    automatic plot generation through post-processing.
    """

    # Plugin metadata
    name = "RPi TKu Telemetry Import (Enhanced)"
    author = "William W. Wallace"
    description = "Import RPi TKu telemetry data files with automatic dataset tagging and metadata"
    file_extensions = set(['.dat'])
    promote_tab = 'telemetry'

    def __init__(self):
        """Initialize the plugin with field definitions."""
        self.fields = [
            field.FieldBool(
                'create_individual_plots',
                descr='Create individual plots for each column',
                default=True
            ),
            field.FieldBool(
                'create_overlay_plots',
                descr='Create overlay plots for voltages, amperages, and state values',
                default=True
            ),
            field.FieldBool(
                'convert_timestamp',
                descr='Convert MJD timestamp to readable datetime string',
                default=True
            ),
            field.FieldBool(
                'include_header_in_notes',
                descr='Include file header information in dataset notes',
                default=True
            ),
            field.FieldText(
                'prefix',
                descr='Prefix to add to dataset names',
                default=''
            ),
            field.FieldText(
                'suffix',
                descr='Suffix to add to dataset names',
                default=''
            ),
        ]
        
        # Instance variables to track metadata
        self.dataset_metadata = {}
        self.plot_instructions = {}
        self.header_info = []

    def mjd_to_datetime(self, mjd_seconds, base_mjd_timestamp):
        """
        Convert MJD seconds offset to datetime string.
        
        Args:
            mjd_seconds: Seconds offset from UTC trigger time.
            base_mjd_timestamp: Unix timestamp of UTC trigger (from file header).
        
        Returns:
            Datetime string in format YYYY-MM-DD HH:MM:SS.
        """
        try:
            base_datetime = datetime.utcfromtimestamp(base_mjd_timestamp)
            result_datetime = base_datetime + timedelta(seconds=float(mjd_seconds))
            return result_datetime.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError, OverflowError):
            return "Invalid"

    def parse_header(self, lines):
        """
        Parse the file header to extract metadata.
        
        Args:
            lines: List of all lines from the file.
        
        Returns:
            Tuple of (header_dict, header_list, column_names, data_start_index, base_mjd_timestamp).
        """
        header_dict = {}
        header_list = []
        column_names = []
        data_start_idx = 0
        base_mjd_timestamp = None

        for i, line in enumerate(lines):
            line = line.rstrip('\r\n')
            
            # Stop at first data line (doesn't start with %)
            if line and not line.startswith('%'):
                data_start_idx = i
                break
            
            # Parse header lines
            if line.startswith('%'):
                # Extract content after % and strip whitespace
                content = line[1:].strip()
                
                if content:
                    header_list.append(content)
                    
                    # Look for specific patterns
                    if 'UTC Trigger Time Stamp' in line:
                        try:
                            parts = content.split('::')
                            if len(parts) > 1:
                                base_mjd_timestamp = float(parts[1].strip())
                        except (ValueError, IndexError):
                            pass
                    
                    # Column headers line (last content line before empty % line)
                    if ',' in content and 'UTC Now minus UTC Trigger' in content:
                        # Parse column names from comma-separated list
                        column_names = [col.strip() for col in content.split(',')]
                
                # Store header lines
                header_dict[f'line_{i}'] = content

        return header_dict, header_list, column_names, data_start_idx, base_mjd_timestamp

    def parse_data_line(self, line):
        """
        Parse a single data line handling both space and column-aligned format.
        
        Args:
            line: String containing a single data row.
        
        Returns:
            List of parsed values.
        """
        # Split by whitespace and filter empty strings
        values = line.split()
        return values

    def categorize_column(self, col_name):
        """
        Determine the category and tags for a column based on its name.
        
        Args:
            col_name: Name of the column.
        
        Returns:
            Dictionary with 'category' and 'tags' keys.
        """
        category = 'other'
        tags = []
        
        # Check for voltage
        if col_name.endswith('V'):
            tags.append('Voltages')
            category = 'voltage'
        
        # Check for amperage (excluding Det*)
        if col_name.endswith('A') and not col_name.startswith('Det'):
            tags.append('Amperages')
            category = 'amperage'
        
        # Check for detector/state values
        if col_name.startswith('Det'):
            tags.append('StateValues')
            category = 'state'
        
        # Check for time-related columns
        if 'time' in col_name.lower() or 'stamp' in col_name.lower() or 'utc' in col_name.lower():
            tags.append('DateTime')
            category = 'datetime'
        
        # Check for other state/boolean columns
        if col_name in ['Lock', 'MIMIC State', 'LOCKED']:
            tags.append('StateValues')
            category = 'state'
        
        return {
            'category': category,
            'tags': tags
        }

    def doImport(self, params):
        """
        Import the RPi TKu telemetry file data.
        
        Returns:
            List of ImportDataset1D and ImportDatasetText objects.
        """
        try:
            # Validate file exists
            if not params.filename or not os.path.exists(params.filename):
                raise ImportPluginException(
                    f"File not found: {params.filename}")

            # Get field values
            field_results = params.field_results
            prefix = field_results.get('prefix', '')
            suffix = field_results.get('suffix', '')
            convert_timestamp = field_results.get('convert_timestamp', True)
            include_header = field_results.get('include_header_in_notes', True)

            # Read the entire file with proper encoding detection
            try:
                with open(params.filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                # Fallback to cp1252 if UTF-8 fails
                with open(params.filename, 'r', encoding='cp1252') as f:
                    lines = f.readlines()

            # Parse header and get column names
            header_dict, header_list, column_names, data_start_idx, base_mjd_timestamp = self.parse_header(lines)

            if not column_names:
                raise ImportPluginException(
                    "Could not parse column headers from file. "
                    "Expected comma-separated list preceded by '%'")

            # Parse data lines
            data_values = []
            for i in range(data_start_idx, len(lines)):
                line = lines[i].rstrip('\r\n')
                if line and not line.startswith('%'):
                    try:
                        values = self.parse_data_line(line)
                        data_values.append(values)
                    except (ValueError, IndexError):
                        # Skip lines that can't be parsed
                        pass

            if not data_values:
                raise ImportPluginException("No data rows found in file")

            # Get base filename for dataset naming
            file_base = os.path.splitext(os.path.basename(params.filename))[0]

            # Helper function to create dataset name
            def make_name(base_name):
                return f"{prefix}{file_base}_{base_name}{suffix}"

            datasets = []
            self.dataset_metadata = {}
            
            # Initialize plot instructions
            self.plot_instructions = {
                'individual_plots': [],
                'voltage_overlay': {'datasets': [], 'title': 'Voltage Values Over Time'},
                'amperage_overlay': {'datasets': [], 'title': 'Amperage Values Over Time'},
                'state_overlay': {'datasets': [], 'title': 'State Values Over Time'},
                'all_data_overlay': {'datasets': [], 'title': 'All Data Over Time'},
                'metadata': {
                    'file_name': os.path.basename(params.filename),
                    'file_base': file_base,
                    'header_lines': header_list,
                    'num_columns': len(column_names),
                    'num_rows': len(data_values),
                    'utc_trigger': base_mjd_timestamp
                }
            }

            # Create datasets for each column
            for col_idx in range(len(column_names)):
                col_name = column_names[col_idx]
                col_data = []

                # Extract column data
                for row_idx in range(len(data_values)):
                    if col_idx < len(data_values[row_idx]):
                        try:
                            # Try to convert to float
                            value = float(data_values[row_idx][col_idx])
                            col_data.append(value)
                        except ValueError:
                            # If not a number, use NaN
                            col_data.append(np.nan)

                # Categorize the column
                col_category = self.categorize_column(col_name)
                
                # Handle special case: convert timestamp to datetime string
                if col_name.startswith('UTC Now minus UTC Trigger') and convert_timestamp and base_mjd_timestamp:
                    # Create datetime string dataset
                    datetime_strings = []
                    for val in col_data:
                        if not np.isnan(val):
                            dt_str = self.mjd_to_datetime(val, base_mjd_timestamp)
                            datetime_strings.append(dt_str)
                        else:
                            datetime_strings.append("Invalid")
                    
                    dataset_name = make_name(f"{col_name}_DateTime")
                    datasets.append(ImportDatasetText(dataset_name, datetime_strings))
                    
                    self.dataset_metadata[dataset_name] = {
                        'original_name': col_name,
                        'type': 'datetime_string',
                        'category': 'datetime',
                        'tags': col_category['tags'],
                        'column_index': col_idx,
                        'notes': 'Converted from MJD offset to ISO datetime format'
                    }
                else:
                    # Regular numeric dataset
                    col_data_array = np.array(col_data)
                    
                    # Skip if all NaN
                    if np.all(np.isnan(col_data_array)):
                        continue

                    dataset_name = make_name(col_name)
                    datasets.append(ImportDataset1D(dataset_name, col_data_array))

                    self.dataset_metadata[dataset_name] = {
                        'original_name': col_name,
                        'type': 'numeric',
                        'category': col_category['category'],
                        'tags': col_category['tags'],
                        'column_index': col_idx,
                        'data_count': np.sum(~np.isnan(col_data_array)),
                        'min': np.nanmin(col_data_array) if not np.all(np.isnan(col_data_array)) else None,
                        'max': np.nanmax(col_data_array) if not np.all(np.isnan(col_data_array)) else None,
                        'mean': np.nanmean(col_data_array) if not np.all(np.isnan(col_data_array)) else None,
                    }

                    # Add to plot instruction lists based on category
                    self.plot_instructions['individual_plots'].append({
                        'dataset': dataset_name,
                        'title': f'{col_name} vs Time'
                    })

                    self.plot_instructions['all_data_overlay']['datasets'].append(dataset_name)

                    if 'Voltages' in col_category['tags']:
                        self.plot_instructions['voltage_overlay']['datasets'].append(dataset_name)
                    
                    if 'Amperages' in col_category['tags']:
                        self.plot_instructions['amperage_overlay']['datasets'].append(dataset_name)
                    
                    if 'StateValues' in col_category['tags']:
                        self.plot_instructions['state_overlay']['datasets'].append(dataset_name)

            if not datasets:
                raise ImportPluginException("No valid data columns found")

            # Store metadata for logging/debugging
            self._import_metadata = {
                'dataset_metadata': self.dataset_metadata,
                'plot_instructions': self.plot_instructions,
                'header_info': header_list
            }

            return datasets

        except ImportPluginException:
            raise
        except Exception as e:
            raise ImportPluginException(f"Error importing file: {str(e)}")

    def getPreview(self, params):
        """
        Generate a preview of what will be imported.
        
        Args:
            params: ImportPluginParams object containing file and field information.
        
        Returns:
            List of preview strings to display to the user.
        """
        try:
            if not params.filename or not os.path.exists(params.filename):
                return ["File not found"]

            # Try UTF-8 first, then fall back to cp1252
            try:
                with open(params.filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(params.filename, 'r', encoding='cp1252') as f:
                    lines = f.readlines()

            header_dict, header_list, column_names, data_start_idx, base_mjd = self.parse_header(lines)

            preview_lines = [
                f"File: {os.path.basename(params.filename)}",
                f"Columns: {len(column_names)}",
                f"Data rows: {len(lines) - data_start_idx}",
                ""
            ]

            if column_names:
                preview_lines.append("Column Names and Classifications:")
                
                voltage_cols = []
                amp_cols = []
                state_cols = []
                other_cols = []
                
                for col in column_names:
                    cat = self.categorize_column(col)
                    if 'Voltages' in cat['tags']:
                        voltage_cols.append(col)
                    elif 'Amperages' in cat['tags']:
                        amp_cols.append(col)
                    elif 'StateValues' in cat['tags']:
                        state_cols.append(col)
                    else:
                        other_cols.append(col)
                
                if voltage_cols:
                    col_str = f"  Voltages ({len(voltage_cols)}): {', '.join(voltage_cols[:5])}"
                    if len(voltage_cols) > 5:
                        col_str += f" ... and {len(voltage_cols)-5} more"
                    preview_lines.append(col_str)
                
                if amp_cols:
                    col_str = f"  Amperages ({len(amp_cols)}): {', '.join(amp_cols[:5])}"
                    if len(amp_cols) > 5:
                        col_str += f" ... and {len(amp_cols)-5} more"
                    preview_lines.append(col_str)
                
                if state_cols:
                    col_str = f"  State Values ({len(state_cols)}): {', '.join(state_cols[:5])}"
                    if len(state_cols) > 5:
                        col_str += f" ... and {len(state_cols)-5} more"
                    preview_lines.append(col_str)
                
                if other_cols:
                    col_str = f"  Other ({len(other_cols)}): {', '.join(other_cols[:5])}"
                    if len(other_cols) > 5:
                        col_str += f" ... and {len(other_cols)-5} more"
                    preview_lines.append(col_str)

            if header_list:
                preview_lines.extend([
                    "",
                    "Header Information:",
                ])
                for header_line in header_list[:5]:
                    if len(header_line) > 80:
                        preview_lines.append(f"  {header_line[:77]}...")
                    else:
                        preview_lines.append(f"  {header_line}")
                if len(header_list) > 5:
                    preview_lines.append(f"  ... and {len(header_list)-5} more header lines")

            return preview_lines

        except Exception as e:
            return [f"Error generating preview: {str(e)}"]


# Register the enhanced plugin
importpluginregistry.append(RPiTKuImportPluginEnhanced)
