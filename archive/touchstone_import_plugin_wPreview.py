
"""
Touchstone Import Plugin for Veusz

This plugin imports Touchstone files (.s1p, .s2p) and generates both
frequency domain and time domain S-parameter data using scikit-rf.

Created by: William W. Wallace
"""

import os
import numpy as np

# Import the necessary Veusz plugin components
from veusz.plugins.importplugin import (
    ImportPlugin, ImportPluginParams, ImportPluginException,
    importpluginregistry
    )
from veusz.plugins import (
    field, ImportDataset1D, ImportFieldInt, ImportDatasetText, ImportField,
    datasetpluginregistry, ImportPluginParams, ImportFieldCheck,
    ImportFieldFloat, ImportFieldText, ImportFieldCombo
                           )

from veusz.plugins.datasetplugin import (Dataset1D)

class TouchstoneImportPlugin(ImportPlugin):
    """Import plugin for Touchstone files (.s1p, .s2p)."""

    # Plugin metadata
    name = "Touchstone Import"
    author = "William W. Wallace"
    description = "Import Touchstone files with frequency and time domain processing"
    file_extensions = set(['.s1p', '.s2p'])
    promote_tab = 'touchstone'

    def __init__(self):
        """Initialize the plugin with field definitions."""

        # Define the input fields for the GUI
        # self.fields = [
        #     field.FieldFilename(
        #         'filename',
        #         descr='Touchstone file to import',
        #         default='',
        #         dialogtitle='Select Touchstone file',
        #         extensions=['.s1p', '.s2p']
        #     ),

        #     field.FieldText(
        #         'prefix',
        #         descr='Prefix to add to dataset names',
        #         default='',
        #         usertext='Dataset prefix:'
        #     ),

        #     field.FieldText(
        #         'suffix',
        #         descr='Suffix to add to dataset names',
        #         default='',
        #         usertext='Dataset suffix:'
        #     ),

        #     field.FieldBool(
        #         'import_time_domain',
        #         descr='Import time domain data',
        #         default=True,
        #         usertext='Import time domain data'
        #     ),

        #     field.FieldBool(
        #         'import_frequency_domain',
        #         descr='Import frequency domain data',
        #         default=True,
        #         usertext='Import frequency domain data'
        #     ),

        #     # Time domain gating parameters
        #     field.FieldFloat(
        #         'gate_center',
        #         descr='Gate center position (ns)',
        #         default=0.0,
        #         usertext='Gate center (ns):'
        #     ),

        #     field.FieldFloat(
        #         'gate_span',
        #         descr='Gate span (ns)',
        #         default=0.2,
        #         usertext='Gate span (ns):'
        #     ),

        #     field.FieldBool(
        #         'enable_gating',
        #         descr='Enable time domain gating',
        #         default=False,
        #         usertext='Enable time domain gating'
        #     ),

        #     # Frequency subdivision parameters
        #     field.FieldText(
        #         'freq_ranges',
        #         descr='Frequency ranges for subdivision (GHz, comma-separated pairs: start1,end1,start2,end2,...)',
        #         default='0,3.6,1.1,3.6,1.6,3.6,1.1,3.0',
        #         usertext='Frequency ranges (GHz):'
        #     ),

        #     field.FieldBool(
        #         'subdivide_frequency',
        #         descr='Create subdivided frequency datasets',
        #         default=True,
        #         usertext='Subdivide frequency ranges'
        #     )
        # ]
        self.fields = [
            field.FieldFilename(
                'filename',
                descr='Touchstone file to import',
                default=''
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

            field.FieldBool(
                'import_time_domain',
                descr='Import time domain data',
                default=True
            ),

            field.FieldBool(
                'import_frequency_domain',
                descr='Import frequency domain data',
                default=True
            ),

            # Time domain gating parameters
            field.FieldFloat(
                'gate_center',
                descr='Gate center position (ns)',
                default=0.0
            ),

            field.FieldFloat(
                'gate_span',
                descr='Gate span (ns)',
                default=0.2
            ),

            field.FieldBool(
                'enable_gating',
                descr='Enable time domain gating',
                default=False
            ),

            # Frequency subdivision parameters
            field.FieldText(
                'freq_ranges',
                descr='Frequency ranges for subdivision (GHz, comma-separated pairs: start1,end1,start2,end2,...)',
                default='0,3.6,1.1,3.6,1.6,3.6,1.1,3.0'
            ),

            field.FieldBool(
                'subdivide_frequency',
                descr='Create subdivided frequency datasets',
                default=True
            )
        ]

    def getPreview(self, params):
        """Generate a preview of what will be imported."""
        try:
            # Basic file validation
            if not params.filename or not os.path.exists(params.filename):
                return []

            # For preview, just show basic info
            preview_lines = [
                f"File: {os.path.basename(params.filename)}",
                f"Format: {'2-port' if params.filename.lower().endswith('.s2p') else '1-port'} Touchstone",
                ""
            ]

            if params.field_results.get('import_frequency_domain', True):
                preview_lines.extend([
                    "Frequency domain datasets:",
                    "  - Frequency values",
                    "  - S11 magnitude (dB)"
                ])

                if params.filename.lower().endswith('.s2p'):
                    preview_lines.extend([
                        "  - S12 magnitude (dB)",
                        "  - S21 magnitude (dB)",
                        "  - S22 magnitude (dB)"
                    ])

            if params.field_results.get('import_time_domain', True):
                preview_lines.extend([
                    "",
                    "Time domain datasets:",
                    "  - Time values",
                    "  - S11 time response (dB)"
                ])

                if params.filename.lower().endswith('.s2p'):
                    preview_lines.extend([
                        "  - S12 time response (dB)",
                        "  - S21 time response (dB)",
                        "  - S22 time response (dB)"
                    ])

            return preview_lines

        except Exception as e:
            return [f"Error generating preview: {str(e)}"]

    def doImport(self, params):
        """Import the Touchstone file data."""
        try:
            # Check if scikit-rf is available
            try:
                import skrf as rf
            except ImportError:
                raise ImportPluginException(
                    "scikit-rf package is required for Touchstone import. "
                    "Please install it using: pip install scikit-rf"
                )

            if not params.filename or not os.path.exists(params.filename):
                raise ImportPluginException(f"File not found: {params.filename}")

            # Load the Touchstone file
            network = rf.Network(params.filename)

            # Get field values
            field_results = params.field_results
            prefix = field_results.get('prefix', '')
            suffix = field_results.get('suffix', '')
            import_freq = field_results.get('import_frequency_domain', True)
            import_time = field_results.get('import_time_domain', True)
            enable_gating = field_results.get('enable_gating', False)
            gate_center = field_results.get('gate_center', 0.0)
            gate_span = field_results.get('gate_span', 0.2)
            subdivide_freq = field_results.get('subdivide_frequency', True)
            freq_ranges_str = field_results.get('freq_ranges', '0,3.6,1.1,3.6,1.6,3.6,1.1,3.0')

            datasets = []

            # Helper function to create dataset name
            def make_name(base_name):
                return f"{prefix}{base_name}{suffix}"

            # Get base filename for dataset naming
            file_base = os.path.splitext(os.path.basename(params.filename))[0]

            # Import frequency domain data
            if import_freq:
                # Frequency array
                freq_hz = network.frequency.f
                freq_ghz = freq_hz / 1e9
                datasets.append(ImportDataset1D(
                    make_name(f"{file_base}_Frequency"),
                    freq_ghz
                ))

                # S-parameters in frequency domain
                if hasattr(network, 's11'):
                    s11_db = network.s11.s_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S11_dB"),
                        s11_db
                    ))

                if hasattr(network, 's12') and network.number_of_ports >= 2:
                    s12_db = network.s12.s_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S12_dB"),
                        s12_db
                    ))

                if hasattr(network, 's21') and network.number_of_ports >= 2:
                    s21_db = network.s21.s_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S21_dB"),
                        s21_db
                    ))

                if hasattr(network, 's22') and network.number_of_ports >= 2:
                    s22_db = network.s22.s_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S22_dB"),
                        s22_db
                    ))

            # Import time domain data
            if import_time:
                # Apply gating if requested
                if enable_gating:
                    try:
                        # Gate the network
                        gated_network = network.time_gate(
                            center=gate_center * 1e-9,  # Convert ns to s
                            span=gate_span * 1e-9       # Convert ns to s
                        )
                        time_network = gated_network
                    except Exception as e:
                        # If gating fails, use original network
                        time_network = network
                        print(f"Warning: Gating failed, using original data: {e}")
                else:
                    time_network = network

                # Time array
                time_ns = time_network.frequency.t_ns
                datasets.append(ImportDataset1D(
                    make_name(f"{file_base}_Time"),
                    time_ns
                ))

                # S-parameters in time domain
                if hasattr(time_network, 's11'):
                    s11_time_db = time_network.s11.s_time_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S11_time_dB"),
                        s11_time_db
                    ))

                if hasattr(time_network, 's12') and time_network.number_of_ports >= 2:
                    s12_time_db = time_network.s12.s_time_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S12_time_dB"),
                        s12_time_db
                    ))

                if hasattr(time_network, 's21') and time_network.number_of_ports >= 2:
                    s21_time_db = time_network.s21.s_time_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S21_time_dB"),
                        s21_time_db
                    ))

                if hasattr(time_network, 's22') and time_network.number_of_ports >= 2:
                    s22_time_db = time_network.s22.s_time_db.flatten()
                    datasets.append(ImportDataset1D(
                        make_name(f"{file_base}_S22_time_dB"),
                        s22_time_db
                    ))

            # Create subdivided frequency datasets if requested
            if subdivide_freq and import_freq:
                try:
                    # Parse frequency ranges
                    freq_values = [float(x.strip()) for x in freq_ranges_str.split(',')]
                    if len(freq_values) % 2 != 0:
                        raise ValueError("Frequency ranges must be pairs of start,end values")

                    # Create frequency range pairs
                    freq_pairs = [(freq_values[i], freq_values[i+1])
                                for i in range(0, len(freq_values), 2)]

                    for i, (start_ghz, end_ghz) in enumerate(freq_pairs):
                        # Create frequency slice
                        freq_slice = network[f"{start_ghz}-{end_ghz}GHz"]

                        # Frequency array for this slice
                        slice_freq_ghz = freq_slice.frequency.f / 1e9
                        datasets.append(ImportDataset1D(
                            make_name(f"{file_base}_Freq_{start_ghz}to{end_ghz}GHz"),
                            slice_freq_ghz
                        ))

                        # S-parameters for this slice
                        if hasattr(freq_slice, 's11'):
                            s11_slice_db = freq_slice.s11.s_db.flatten()
                            datasets.append(ImportDataset1D(
                                make_name(f"{file_base}_S11_{start_ghz}to{end_ghz}GHz_dB"),
                                s11_slice_db
                            ))

                        if hasattr(freq_slice, 's12') and freq_slice.number_of_ports >= 2:
                            s12_slice_db = freq_slice.s12.s_db.flatten()
                            datasets.append(ImportDataset1D(
                                make_name(f"{file_base}_S12_{start_ghz}to{end_ghz}GHz_dB"),
                                s12_slice_db
                            ))

                        if hasattr(freq_slice, 's21') and freq_slice.number_of_ports >= 2:
                            s21_slice_db = freq_slice.s21.s_db.flatten()
                            datasets.append(ImportDataset1D(
                                make_name(f"{file_base}_S21_{start_ghz}to{end_ghz}GHz_dB"),
                                s21_slice_db
                            ))

                        if hasattr(freq_slice, 's22') and freq_slice.number_of_ports >= 2:
                            s22_slice_db = freq_slice.s22.s_db.flatten()
                            datasets.append(ImportDataset1D(
                                make_name(f"{file_base}_S22_{start_ghz}to{end_ghz}GHz_dB"),
                                s22_slice_db
                            ))

                        # Time domain for this slice if requested
                        if import_time:
                            slice_time_ns = freq_slice.frequency.t_ns
                            datasets.append(ImportDataset1D(
                                make_name(f"{file_base}_Time_{start_ghz}to{end_ghz}GHz_ns"),
                                slice_time_ns
                            ))

                            if hasattr(freq_slice, 's11'):
                                s11_slice_time_db = freq_slice.s11.s_time_db.flatten()
                                datasets.append(ImportDataset1D(
                                    make_name(f"{file_base}_S11_{start_ghz}to{end_ghz}GHz_time_dB"),
                                    s11_slice_time_db
                                ))

                            if hasattr(freq_slice, 's12') and freq_slice.number_of_ports >= 2:
                                s12_slice_time_db = freq_slice.s12.s_time_db.flatten()
                                datasets.append(ImportDataset1D(
                                    make_name(f"{file_base}_S12_{start_ghz}to{end_ghz}GHz_time_dB"),
                                    s12_slice_time_db
                                ))

                            if hasattr(freq_slice, 's21') and freq_slice.number_of_ports >= 2:
                                s21_slice_time_db = freq_slice.s21.s_time_db.flatten()
                                datasets.append(ImportDataset1D(
                                    make_name(f"{file_base}_S21_{start_ghz}to{end_ghz}GHz_time_dB"),
                                    s21_slice_time_db
                                ))

                            if hasattr(freq_slice, 's22') and freq_slice.number_of_ports >= 2:
                                s22_slice_time_db = freq_slice.s22.s_time_db.flatten()
                                datasets.append(ImportDataset1D(
                                    make_name(f"{file_base}_S22_{start_ghz}to{end_ghz}GHz_time_dB"),
                                    s22_slice_time_db
                                ))

                except Exception as e:
                    print(f"Warning: Frequency subdivision failed: {e}")

            return datasets

        except ImportPluginException:
            raise
        except Exception as e:
            raise ImportPluginException(f"Error importing Touchstone file: {str(e)}")

# Register the plugin
importpluginregistry.append(TouchstoneImportPlugin)
