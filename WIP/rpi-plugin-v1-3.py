"""
RPi TKu Telemetry File Import Plugin for Veusz 4.2 - ENHANCED PRODUCTION VERSION

This plugin imports RPi TKu telemetry data files (.dat) and automatically:
- Creates datasets for each column with appropriate naming
- Tags voltage datasets (ending in 'V') with "Voltages"
- Tags amperage datasets (ending in 'A') with "Amperages"
- Tags state/detector datasets (starting with 'Det') with "StateValues"
- Tags datetime columns with "DateTime"
- Converts MJD timestamps to readable YYYY-MM-DD HH:MM:SS format
- Tracks comprehensive metadata for each dataset
- Stores statistical information (min, max, mean, count)
- Preserves header information with dataset notes
- Enables post-processing plot generation or data analysis

Created by: William W. Wallace
Modified for: RPi TKu telemetry files
Version: 1.3 (Enhanced with Full Metadata Tracking)
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
    
    Provides comprehensive metadata tracking, statistical analysis,
    and intelligent dataset organization through tagging and notes.
    """

    # Plugin metadata
    name = "RPi TKu Telemetry Import (Enhanced)"
    author = "William W. Wallace"
    description = "Import RPi TKu telemetry data files with metadata tracking and dataset tagging"
    file_extensions = set(['.dat'])
    promote_tab = 'telemetry'

    def __init__(self):
        """Initialize the plugin with field definitions."""
        self.fields = [
            field.FieldBool(
                'convert_timestamp',
                descr='Convert MJD timestamp to readable datetime string',
                default=True
            ),
            field.FieldBool(
                'store_statistics',
                descr='Calculate and store statistics (min, max, mean) for numeric datasets',
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
        self.import_summary = {}
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
            Tuple of (header_list, column_names, data_start_index, base_mjd_timestamp).
        """
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

        return header_list, column_names, data_start_idx, base_mjd_timestamp

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
            if 'StateValues' not in tags:
                tags.append('StateValues')
            category = 'state'
        
        return {
            'category': category,
            'tags': tags
        }

    def calculate_statistics(self, data_array):
        """
        Calculate statistical measures for a numeric dataset.
        
        Args:
            data_array: NumPy array of numeric data.
        
        Returns:
            Dictionary with statistical information.
        """
        valid_data = data_array[~np.isnan(data_array)]
        
        if len(valid_data) == 0:
            return {
                'count': 0,
                'valid_count': 0,
                'nan_count': len(data_array),
                'min': None,
                'max': None,
                'mean': None,
                'std': None,
            }
        
        return {
            'count': len(data_array),
            'valid_count': len(valid_data),
            'nan_count': np.sum(np.isnan(data_array)),
            'min': float(np.nanmin(data_array)),
            'max': float(np.nanmax(data_array)),
            'mean': float(np.nanmean(data_array)),
            'std': float(np.nanstd(data_array)),
        }

    def create_dataset_note(self, original_name, col_category, statistics=None, header_lines=None):
        """
        Create informative notes for a dataset.
        
        Args:
            original_name: Original column name from file.
            col_category: Category dictionary from categorize_column().
            statistics: Optional statistics dictionary.
            header_lines: Optional list of header lines.
        
        Returns:
            String with formatted notes.
        """
        notes = []
        notes.append(f"Original column: {original_name}")
        
        if col_category['category'] != 'other':
            notes.append(f"Category: {col_category['category'].title()}")
        
        if col_category['tags']:
            notes.append(f"Tags: {', '.join(col_category['tags'])}")
        
        if statistics:
            notes.append("")
            notes.append("Statistics:")
            if statistics['valid_count'] > 0:
                notes.append(f"  Valid points: {statistics['valid_count']}")
                notes.append(f"  Missing values: {statistics['nan_count']}")
                notes.append(f"  Min: {statistics['min']:.6g}")
                notes.append(f"  Max: {statistics['max']:.6g}")
                notes.append(f"  Mean: {statistics['mean']:.6g}")
                notes.append(f"  Std Dev: {statistics['std']:.6g}")
            else:
                notes.append("  All values are NaN")
        
        if header_lines:
            notes.append("")
            notes.append("File Header Information:")
            for header_line in header_lines[:5]:
                if len(header_line) > 70:
                    notes.append(f"  {header_line[:67]}...")
                else:
                    notes.append(f"  {header_line}")
            if len(header_lines) > 5:
                notes.append(f"  ... and {len(header_lines)-5} more header lines")
        
        return "\n".join(notes)

    def doImport(self, params):
        """
        Import the RPi TKu telemetry file data.
        
        Args:
            params: ImportPluginParams object
        
        Returns:
            List of ImportDataset1D and ImportDatasetText objects.
        """
        try:
            # Validate file exists
            if not params.filename or not os.path.exists(params.filename):
                raise ImportPluginException(
                    f"File not found: {params.filename}")

            # Get field values using proper Veusz API
            prefix = params.field_results.get('prefix', '')
            suffix = params.field_results.get('suffix', '')
            convert_timestamp = params.field_results.get('convert_timestamp', True)
            store_statistics = params.field_results.get('store_statistics', True)
            include_header = params.field_results.get('include_header_in_notes', True)

            # Read the entire file with proper encoding detection
            lines = []
            for encoding in ['utf-8', 'cp1252', 'latin-1']:
                try:
                    with open(params.filename, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue

            if not lines:
                raise ImportPluginException("Could not read file with any encoding")

            # Parse header and get column names
            header_list, column_names, data_start_idx, base_mjd_timestamp = self.parse_header(lines)
            self.header_info = header_list

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
            
            # Initialize import summary
            self.import_summary = {
                'file_name': os.path.basename(params.filename),
                'file_base': file_base,
                'num_columns': len(column_names),
                'num_rows': len(data_values),
                'timestamp': datetime.now().isoformat(),
                'utc_trigger': base_mjd_timestamp,
                'datasets_created': 0,
                'category_counts': {
                    'voltages': 0,
                    'amperages': 0,
                    'state_values': 0,
                    'datetime': 0,
                    'other': 0,
                },
            }

            # Create datasets for each column
            for col_idx in range(len(column_names)):
                col_name = column_names[col_idx]
                col_data = []

                # Extract column data
                for row_idx in range(len(data_values)):
                    if col_idx < len(data_values[row_idx]):
                        try:
                            value = float(data_values[row_idx][col_idx])
                            col_data.append(value)
                        except ValueError:
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
                    dataset = ImportDatasetText(dataset_name, datetime_strings)
                    
                    # Add tags and notes
                    if col_category['tags']:
                        dataset.tags = col_category['tags']
                    
                    # Create notes with header info if requested
                    notes = self.create_dataset_note(
                        col_name,
                        col_category,
                        statistics=None,
                        header_lines=header_list if include_header else None
                    )
                    if notes:
                        dataset.notes = notes
                    
                    datasets.append(dataset)
                    
                    # Track metadata
                    self.dataset_metadata[dataset_name] = {
                        'original_name': col_name,
                        'type': 'datetime_string',
                        'category': 'datetime',
                        'tags': col_category['tags'],
                        'column_index': col_idx,
                        'data_count': len(datetime_strings),
                        'notes': notes if notes else None,
                    }
                    
                    self.import_summary['datasets_created'] += 1
                    self.import_summary['category_counts']['datetime'] += 1
                    
                else:
                    # Regular numeric dataset
                    col_data_array = np.array(col_data)
                    
                    # Skip if all NaN
                    if np.all(np.isnan(col_data_array)):
                        continue

                    dataset_name = make_name(col_name)
                    dataset = ImportDataset1D(dataset_name, col_data_array)

                    # Add tags
                    if col_category['tags']:
                        dataset.tags = col_category['tags']
                    
                    # Calculate statistics if requested
                    statistics = None
                    if store_statistics:
                        statistics = self.calculate_statistics(col_data_array)
                    
                    # Create notes with header info if requested
                    notes = self.create_dataset_note(
                        col_name,
                        col_category,
                        statistics=statistics,
                        header_lines=header_list if include_header else None
                    )
                    if notes:
                        dataset.notes = notes
                    
                    datasets.append(dataset)

                    # Track metadata
                    self.dataset_metadata[dataset_name] = {
                        'original_name': col_name,
                        'type': 'numeric',
                        'category': col_category['category'],
                        'tags': col_category['tags'],
                        'column_index': col_idx,
                        'statistics': statistics,
                        'notes': notes if notes else None,
                    }

                    self.import_summary['datasets_created'] += 1
                    
                    # Track category counts
                    if col_category['category'] == 'voltage':
                        self.import_summary['category_counts']['voltages'] += 1
                    elif col_category['category'] == 'amperage':
                        self.import_summary['category_counts']['amperages'] += 1
                    elif col_category['category'] == 'state':
                        self.import_summary['category_counts']['state_values'] += 1
                    elif col_category['category'] == 'datetime':
                        self.import_summary['category_counts']['datetime'] += 1
                    else:
                        self.import_summary['category_counts']['other'] += 1

            if not datasets:
                raise ImportPluginException("No valid data columns found")

            return datasets

        except ImportPluginException:
            raise
        except Exception as e:
            raise ImportPluginException(f"Error importing file: {str(e)}")

    def getPreview(self, params):
        """
        Generate a preview of what will be imported.
        
        Args:
            params: ImportPluginParams object
        
        Returns:
            List of preview strings to display to the user.
        """
        try:
            if not params.filename or not os.path.exists(params.filename):
                return ["File not found"]

            # Try reading with multiple encodings
            lines = []
            for encoding in ['utf-8', 'cp1252', 'latin-1']:
                try:
                    with open(params.filename, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue

            if not lines:
                return ["Could not read file with any encoding"]

            header_list, column_names, data_start_idx, base_mjd = self.parse_header(lines)

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
                datetime_cols = []
                other_cols = []
                
                for col in column_names:
                    cat = self.categorize_column(col)
                    if 'Voltages' in cat['tags']:
                        voltage_cols.append(col)
                    elif 'Amperages' in cat['tags']:
                        amp_cols.append(col)
                    elif 'StateValues' in cat['tags']:
                        state_cols.append(col)
                    elif 'DateTime' in cat['tags']:
                        datetime_cols.append(col)
                    else:
                        other_cols.append(col)
                
                if voltage_cols:
                    col_str = f"  Voltages ({len(voltage_cols)}): {', '.join(voltage_cols[:3])}"
                    if len(voltage_cols) > 3:
                        col_str += f" ... +{len(voltage_cols)-3} more"
                    preview_lines.append(col_str)
                
                if amp_cols:
                    col_str = f"  Amperages ({len(amp_cols)}): {', '.join(amp_cols[:3])}"
                    if len(amp_cols) > 3:
                        col_str += f" ... +{len(amp_cols)-3} more"
                    preview_lines.append(col_str)
                
                if state_cols:
                    col_str = f"  State Values ({len(state_cols)}): {', '.join(state_cols[:3])}"
                    if len(state_cols) > 3:
                        col_str += f" ... +{len(state_cols)-3} more"
                    preview_lines.append(col_str)
                
                if datetime_cols:
                    col_str = f"  DateTime ({len(datetime_cols)}): {', '.join(datetime_cols[:2])}"
                    if len(datetime_cols) > 2:
                        col_str += f" ... +{len(datetime_cols)-2} more"
                    preview_lines.append(col_str)
                
                if other_cols:
                    col_str = f"  Other ({len(other_cols)}): {', '.join(other_cols[:3])}"
                    if len(other_cols) > 3:
                        col_str += f" ... +{len(other_cols)-3} more"
                    preview_lines.append(col_str)

            if header_list:
                preview_lines.append("")
                preview_lines.append("Header Information:")
                for header_line in header_list[:3]:
                    if len(header_line) > 70:
                        preview_lines.append(f"  {header_line[:67]}...")
                    else:
                        preview_lines.append(f"  {header_line}")
                if len(header_list) > 3:
                    preview_lines.append(f"  ... and {len(header_list)-3} more header lines")

            return preview_lines

        except Exception as e:
            return [f"Error generating preview: {str(e)}"]


# Register the plugin
importpluginregistry.append(RPiTKuImportPluginEnhanced)
