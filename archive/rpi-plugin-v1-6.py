"""
RPi TKu Telemetry File Import Plugin for Veusz 4.2 - FINAL WORKING VERSION

This plugin imports RPi TKu telemetry data files (.dat) with:
- Full metadata tracking
- Statistical analysis engine
- Intelligent dataset organization

CRITICAL: Fixed doImport() signature to match Veusz 4.2 API exactly.
The issue was that Veusz 4.2 passes prefix/suffix both as args and kwargs.

Created by: William W. Wallace
Version: 1.6 (Veusz 4.2 Final Fix)
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
    
    Provides comprehensive metadata tracking and statistical analysis.
    Fully compatible with Veusz 4.2.
    """

    # Plugin metadata
    name = "RPi TKu Telemetry Import (Enhanced)"
    author = "William W. Wallace"
    description = "Import RPi TKu telemetry data files with metadata tracking and statistics"
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

    def mjd_to_datetime(self, mjd_seconds, base_mjd_timestamp):
        """Convert MJD seconds offset to datetime string."""
        try:
            base_datetime = datetime.utcfromtimestamp(base_mjd_timestamp)
            result_datetime = base_datetime + timedelta(seconds=float(mjd_seconds))
            return result_datetime.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError, OverflowError):
            return "Invalid"

    def parse_header(self, lines):
        """Parse the file header to extract metadata."""
        header_list = []
        column_names = []
        data_start_idx = 0
        base_mjd_timestamp = None

        for i, line in enumerate(lines):
            line = line.rstrip('\r\n')
            
            # Stop at first data line
            if line and not line.startswith('%'):
                data_start_idx = i
                break
            
            # Parse header lines
            if line.startswith('%'):
                content = line[1:].strip()
                
                if content:
                    header_list.append(content)
                    
                    # Look for UTC Trigger timestamp
                    if 'UTC Trigger Time Stamp' in line:
                        try:
                            parts = content.split('::')
                            if len(parts) > 1:
                                base_mjd_timestamp = float(parts[1].strip())
                        except (ValueError, IndexError):
                            pass
                    
                    # Extract column names
                    if ',' in content and 'UTC Now minus UTC Trigger' in content:
                        column_names = [col.strip() for col in content.split(',')]

        return header_list, column_names, data_start_idx, base_mjd_timestamp

    def parse_data_line(self, line):
        """Parse a single data line."""
        values = line.split()
        return values

    def categorize_column(self, col_name):
        """Determine category and tags for a column."""
        tags = []
        
        if col_name.endswith('V'):
            tags.append('Voltages')
        
        if col_name.endswith('A') and not col_name.startswith('Det'):
            tags.append('Amperages')
        
        if col_name.startswith('Det'):
            tags.append('StateValues')
        
        if 'time' in col_name.lower() or 'utc' in col_name.lower():
            tags.append('DateTime')
        
        if col_name in ['Lock', 'MIMIC State', 'LOCKED']:
            if 'StateValues' not in tags:
                tags.append('StateValues')
        
        return tags

    def calculate_statistics(self, data_array):
        """Calculate statistical measures for a numeric dataset."""
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

    def create_dataset_note(self, original_name, tags, statistics=None, header_lines=None):
        """Create informative notes for a dataset."""
        notes = []
        notes.append(f"Original column: {original_name}")
        
        if tags:
            notes.append(f"Tags: {', '.join(tags)}")
        
        if statistics and statistics['valid_count'] > 0:
            notes.append("")
            notes.append("Statistics:")
            notes.append(f"  Valid points: {statistics['valid_count']}")
            notes.append(f"  Missing values: {statistics['nan_count']}")
            notes.append(f"  Min: {statistics['min']:.6g}")
            notes.append(f"  Max: {statistics['max']:.6g}")
            notes.append(f"  Mean: {statistics['mean']:.6g}")
            notes.append(f"  Std Dev: {statistics['std']:.6g}")
        
        if header_lines:
            notes.append("")
            notes.append("File Header:")
            for header_line in header_lines[:3]:
                if len(header_line) > 70:
                    notes.append(f"  {header_line[:67]}...")
                else:
                    notes.append(f"  {header_line}")
        
        return "\n".join(notes)

    def doImport(self, doc, filename, linked, encoding, prefix, suffix, tags, fields):
        """
        Import the RPi TKu telemetry file data.
        
        CRITICAL: Signature matches Veusz 4.2 API exactly.
        Veusz passes prefix/suffix as positional args, so we accept them that way.
        """
        try:
            if not filename or not os.path.exists(filename):
                raise ImportPluginException(f"File not found: {filename}")

            # Get field values from fields dict (Veusz 4.2 passes them here)
            convert_timestamp = fields.get('convert_timestamp', True)
            store_statistics = fields.get('store_statistics', True)
            include_header = fields.get('include_header_in_notes', True)

            # Read file with encoding detection
            lines = []
            for enc in ['utf-8', 'cp1252', 'latin-1']:
                try:
                    with open(filename, 'r', encoding=enc) as f:
                        lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue

            if not lines:
                raise ImportPluginException("Could not read file with any encoding")

            # Parse header
            header_list, column_names, data_start_idx, base_mjd_timestamp = self.parse_header(lines)

            if not column_names:
                raise ImportPluginException("Could not parse column headers")

            # Parse data
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
                raise ImportPluginException("No data rows found")

            # Get filename base
            file_base = os.path.splitext(os.path.basename(filename))[0]
            
            def make_name(base_name):
                return f"{prefix}{file_base}_{base_name}{suffix}"

            datasets = []

            # Create datasets
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

                # Get tags
                col_tags = self.categorize_column(col_name)
                
                # Handle timestamp conversion
                if col_name.startswith('UTC Now minus UTC Trigger') and convert_timestamp and base_mjd_timestamp:
                    datetime_strings = []
                    for val in col_data:
                        if not np.isnan(val):
                            dt_str = self.mjd_to_datetime(val, base_mjd_timestamp)
                            datetime_strings.append(dt_str)
                        else:
                            datetime_strings.append("Invalid")
                    
                    dataset_name = make_name(f"{col_name}_DateTime")
                    dataset = ImportDatasetText(dataset_name, datetime_strings)
                    
                    if col_tags:
                        dataset.tags = col_tags
                    
                    notes = self.create_dataset_note(col_name, col_tags, None, header_list if include_header else None)
                    if notes:
                        dataset.notes = notes
                    
                    datasets.append(dataset)
                    
                else:
                    # Regular numeric dataset
                    col_data_array = np.array(col_data)
                    
                    if np.all(np.isnan(col_data_array)):
                        continue

                    dataset_name = make_name(col_name)
                    dataset = ImportDataset1D(dataset_name, col_data_array)

                    if col_tags:
                        dataset.tags = col_tags
                    
                    # Calculate statistics if requested
                    statistics = None
                    if store_statistics:
                        statistics = self.calculate_statistics(col_data_array)
                    
                    notes = self.create_dataset_note(col_name, col_tags, statistics, header_list if include_header else None)
                    if notes:
                        dataset.notes = notes
                    
                    datasets.append(dataset)

            if not datasets:
                raise ImportPluginException("No valid data columns found")

            return datasets

        except ImportPluginException:
            raise
        except Exception as e:
            raise ImportPluginException(f"Import error: {str(e)}")


# Register the plugin
importpluginregistry.append(RPiTKuImportPluginEnhanced)
