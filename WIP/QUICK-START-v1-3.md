# RPi TKu Telemetry Import Plugin - Enhanced Quick Start Guide (v1.3)

## ⚠️ IMPORTANT: Use the ENHANCED VERSION with Full Metadata Tracking

We've created an enhanced version (v1.3) with comprehensive metadata tracking, statistical analysis, and intelligent dataset organization.

### Download the Enhanced Plugin

**Use this file**: `rpi-plugin-v1-3.py` (Version 1.3 - Enhanced Production Version)

---

## 🎯 What's New in Version 1.3

### Enhanced Features

✅ **Comprehensive Metadata Tracking**
- Original column names preserved in dataset notes
- File header information stored with each dataset
- Import timestamp and summary statistics tracked

✅ **Statistical Analysis**
- Automatic min/max/mean/std calculation for numeric datasets
- Valid data point counting
- NaN value tracking and reporting

✅ **Intelligent Dataset Notes**
- Each dataset includes formatted notes with:
  - Original column name
  - Category classification
  - Applied tags
  - Complete statistics (when enabled)
  - File header context

✅ **Configurable Options**
- Toggle timestamp conversion
- Toggle statistics calculation
- Toggle header information inclusion
- Custom prefix/suffix for dataset names

---

## ⚡ Installation (2 Minutes)

### Step 1: Locate Your Veusz Plugins Directory

**Windows:**
```
%APPDATA%\Veusz\plugins\
or
C:\Users\[YourUsername]\AppData\Roaming\Veusz\plugins\
```

**Linux:**
```
~/.veusz/plugins/
```

**macOS:**
```
~/Library/Application Support/Veusz/plugins/
```

### Step 2: Download and Install the Enhanced Version

1. **Download**: `rpi-plugin-v1-3.py` (Version 1.3 - Enhanced)
2. **Rename** to: `rpi_tku_import_plugin.py` (remove dashes, use underscores)
3. **Delete** all old versions completely:
   - Delete `rpi-plugin-corrected.py` if present
   - Delete `rpi-plugin-fixed.py` if present
   - Delete `rpi-plugin-enhanced.py` if present
   - Delete any previously installed version
4. **Copy** the enhanced version to your plugins directory
5. **Restart Veusz completely** (close all windows)

### Step 3: Verify Installation

1. Open Veusz
2. Click **Data** menu
3. Click **Import** submenu
4. You should see: **"RPi TKu Telemetry Import (Enhanced)"** ✅
5. Click to select it - preview should appear without errors

---

## 🚀 First Import (5 Minutes)

### Import Your Data

1. In Veusz: **Data** → **Import** → **RPi TKu Telemetry Import (Enhanced)**
2. A tab for the plugin should appear with options
3. Click **Browse** and select your `.dat` file
4. **Review the preview section** (should show column classifications without errors) ✅
5. Configure options:
   - ✓ **Convert timestamp**: Checked (creates human-readable dates)
   - ✓ **Store statistics**: Checked (calculates min/max/mean for each dataset)
   - ✓ **Include header in notes**: Checked (adds file header context)
   - **Prefix**: Leave empty (or add date like `2025_12_10_`)
   - **Suffix**: Leave empty (optional)
6. Click **OK** to import

✅ Import should complete successfully!

### View Imported Datasets

1. Click **Data** → **List Datasets**
2. You'll see all your columns imported as datasets
3. Notice the automatic tags:
   - 🟦 **Voltages** (columns ending in 'V')
   - 🔴 **Amperages** (columns ending in 'A')
   - ⚙️ **StateValues** (detector columns)
   - 📅 **DateTime** (timestamp columns)

### View Dataset Notes with Statistics

1. In **Data → List Datasets**, select any dataset
2. Click the **Notes** tab at the bottom
3. You'll see:
   - Original column name
   - Category and tags
   - **Statistics** section with:
     - Valid data points count
     - Missing values (NaN) count
     - Minimum value
     - Maximum value
     - Mean (average)
     - Standard deviation
   - File header context

**Example Dataset Notes:**
```
Original column: PS1CH1V
Category: Voltage
Tags: Voltages

Statistics:
  Valid points: 1024
  Missing values: 0
  Min: 11.85
  Max: 12.15
  Mean: 12.00
  Std Dev: 0.087

File Header Information:
  RPi TKu Detector Electronics Telemetry Data
  UTC Trigger Time Stamp:: 1702262400.0
  ... and 3 more header lines
```

---

## 📊 Create Your First Plot (3 Minutes)

### Plot Voltages Over Time

1. Click **Insert** → **Graph** (or toolbar button)
2. In the graph properties panel:
   - **X-axis dataset**: Select `Rpi_TKu_file_UTC Now minus UTC Trigger (sec)`
   - Click the **+** button to add Y-axis datasets
   - **Y-axis datasets**: Select multiple voltage columns:
     - `Rpi_TKu_file_PS1CH1V`
     - `Rpi_TKu_file_PS1CH2V`
     - `Rpi_TKu_file_PS1CH3V`
     - `Rpi_TKu_file_PS1CH4V`
     - (and more if desired)
3. Right-click the graph → **Properties**
4. Add a title: "Power Supply Voltages Over Time"
5. Enable legend: Check "Show legend"

**Result**: You now have a plot showing all power supply voltages overlaid!

---

## 📋 What Gets Imported

From your `.dat` file, the plugin creates:

### Voltage Datasets (Tagged: "Voltages")
- `Rpi_TKu_file_PS1CH1V` through `PS2CH1V`
- `Rpi_TKu_file_Det +3.3V`, `Det -5V`, `Det +5V`
- Each includes statistics: min, max, mean, std deviation

### Amperage Datasets (Tagged: "Amperages")
- `Rpi_TKu_file_PS1CH1A` through `PS2CH1A`
- Complete statistical analysis for current measurements

### State/Detector Datasets (Tagged: "StateValues")
- `Rpi_TKu_file_Det PreAmp`, `Det HPA`, `Det AWG`
- `Rpi_TKu_file_Lock`, `MIMIC State`
- Statistics show valid/invalid transitions

### DateTime Datasets (Tagged: "DateTime")
- `Rpi_TKu_file_UTC Now minus UTC Trigger (sec)_DateTime`
- Converted to YYYY-MM-DD HH:MM:SS format
- Includes file header context in notes

### Other Numeric Columns
- `Rpi_TKu_file_TFOM`, `Year`, `DOY`, `AGC`, etc.
- Each with full statistical information

---

## 🎯 Advanced Features

### Using Dataset Notes for Analysis

The enhanced metadata in dataset notes enables:

**1. Quick Quality Assessment**
- View valid vs NaN count to check data completeness
- Standard deviation indicates data stability
- Min/max shows measurement ranges

**2. Data Validation**
- Verify expected min/max values are reasonable
- Check for anomalies (unusual std deviation)
- Identify columns with all NaN values

**3. Documentation**
- File header context available in every dataset
- Original column names preserved for reference
- Complete metadata trail for reproducibility

### Configurable Import Options

**When to toggle options:**

- **Convert timestamp**: Uncheck only if you need raw seconds values
- **Store statistics**: Uncheck for faster import of very large files
- **Include header in notes**: Uncheck to reduce note length for many columns

---

## ⚠️ Troubleshooting

### Error: "too many values to unpack"

**Problem**: Got an error during import

**Solution**: 
✅ You were using an OLD version. Use the **ENHANCED version** (v1.3):
1. Download `rpi-plugin-v1-3.py` (Version 1.3)
2. Rename to `rpi_tku_import_plugin.py`
3. **Delete all old versions** completely
4. Copy the enhanced version to plugins directory
5. Restart Veusz completely

### Plugin Doesn't Appear in Menu

**Problem**: Can't find "RPi TKu Telemetry Import" in Data → Import menu

**Solutions**:
1. ✅ Verify file is named: `rpi_tku_import_plugin.py` (underscores only)
2. ✅ Verify it's in correct plugins directory
3. ✅ **Completely restart Veusz** (close all windows)
4. ✅ Delete any old versions that might be conflicting
5. ✅ Make sure you're using **v1.3 (rpi-plugin-v1-3.py)**

### Preview Shows Error

**Problem**: Preview section shows an error message

**Solution**:
1. ✅ Make sure you're using **v1.3 (rpi-plugin-v1-3.py)**
2. ✅ Delete old versions and reinstall enhanced version
3. ✅ File encoding is auto-detected (UTF-8, cp1252, latin-1)

### "Could Not Parse Column Headers"

**Problem**: Plugin can't read the file format

**Solutions**:
1. ✅ Verify file format:
   - Lines 1-8: Header with % prefix
   - Line 9: Comma-separated column names
   - Line 10: Just `%` (empty marker)
   - Line 11+: Data rows
2. ✅ Don't edit .dat files in Excel (corrupts format)

### Dataset Notes Show Incomplete Statistics

**Problem**: Some datasets missing statistical information

**Solution**:
✅ This is normal for:
- Text datasets (converted datetime)
- Columns with all NaN values
- When "Store statistics" option is unchecked

---

## 💡 Tips & Best Practices

### 1. Always Preview First
Before importing, the preview section shows:
- File name and statistics
- Column count and data row count
- Classification of columns by type

### 2. Review Dataset Notes Immediately
After importing:
1. Open Data → List Datasets
2. Select any dataset
3. View the Notes tab
4. Check statistics for data quality assessment

### 3. Use Prefixes for Organization
When importing multiple files, use date-based prefixes:
- Prefix: `2025_12_10_`
- Prefix: `2025_12_11_`
- Results in: `2025_12_10_Rpi_TKu_file_PS1CH1V`

### 4. Organize by Tags
Tags help you find related data:
- Filter by "Voltages" to see all power rails
- Filter by "Amperages" to see all current measurements
- Filter by "StateValues" to see detector status
- Filter by "DateTime" to see timestamp data

### 5. Export Notes for Documentation
To create documentation:
1. View dataset in Data → List Datasets
2. Copy the Notes content
3. Paste into your analysis document
4. References original file and all statistics

### 6. Save Your Work
After creating plots, save the Veusz document:
- **File** → **Save As**
- All datasets and plots are preserved
- Notes and statistics are retained

---

## 📚 Next Steps

After your first import:

1. **Review Statistics** - Check dataset notes for quality metrics
2. **Create Plots** - Use the tagged datasets to create analysis visualizations
3. **Export Notes** - Document your data source and quality metrics
4. **Analyze Trends** - Use min/max/mean values to understand data ranges
5. **Generate Reports** - Export plots and notes for sharing

---

## 🔧 Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.3** | 2025-01-07 | ✅ Full metadata tracking, statistics, notes, configurable options |
| 1.2 | 2025-01-07 | Fixed API field retrieval issue |
| 1.1 | 2025-12-10 | Fixed "too many values" error |
| 1.0 | 2025-12-10 | Initial release |

---

## ✅ Verification Checklist

After installation, verify:
- [ ] Plugin appears in Data → Import menu
- [ ] Plugin name is "RPi TKu Telemetry Import (Enhanced)"
- [ ] Preview section appears without errors
- [ ] File selection works
- [ ] Column classification shows in preview
- [ ] Import completes without errors
- [ ] Datasets appear in Data → List Datasets
- [ ] Datasets have proper tags (Voltages, Amperages, etc.)
- [ ] Dataset notes contain original column names
- [ ] Statistics appear in notes (min, max, mean, std)
- [ ] File header information appears in notes

---

**Plugin Version**: 1.3 (Enhanced Production)  
**Compatible with**: Veusz 4.2+  
**Created**: 2025-12-10  
**Last Enhanced**: 2025-01-07

**Ready to use! Download rpi-plugin-v1-3.py and enjoy professional-grade telemetry analysis! 📊**
