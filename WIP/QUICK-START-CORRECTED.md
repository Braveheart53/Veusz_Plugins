# RPi TKu Telemetry Import Plugin - Quick Start Guide (CORRECTED)

## ⚠️ IMPORTANT: Use the CORRECTED Version

We've identified and fixed the issue causing the "too many values to unpack" error.

### Download the Corrected Plugin

**Use this file**: `rpi-plugin-corrected.py` (Version 1.2 - Latest corrected version)

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

### Step 2: Download and Install the CORRECTED Version

1. **Download**: `rpi-plugin-corrected.py` (the corrected version - Version 1.2)
2. **Rename** to: `rpi_tku_import_plugin.py` (remove dashes, use underscores)
3. **Delete** all old versions:
   - Delete `rpi-plugin-enhanced.py` if present
   - Delete `rpi-plugin-fixed.py` if present
   - Delete any previously installed version
4. **Copy** the corrected version to your plugins directory
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

### Amperage Datasets (Tagged: "Amperages")
- `Rpi_TKu_file_PS1CH1A` through `PS2CH1A`

### State/Detector Datasets (Tagged: "StateValues")
- `Rpi_TKu_file_Det PreAmp`, `Det HPA`, `Det AWG`
- `Rpi_TKu_file_Lock`, `MIMIC State`

### DateTime Datasets (Tagged: "DateTime")
- `Rpi_TKu_file_UTC Now minus UTC Trigger (sec)_DateTime`
- (Converted to YYYY-MM-DD HH:MM:SS format)

### Other Numeric Columns
- `Rpi_TKu_file_TFOM`, `Year`, `DOY`, `AGC`, etc.

---

## ⚠️ Troubleshooting

### Error: "too many values to unpack"

**Problem**: Got an error during import preview or selection

**Solution**: 
✅ You were using an OLD version. Use the **CORRECTED version** (v1.2):
1. Download `rpi-plugin-corrected.py` (the latest version)
2. Rename to `rpi_tku_import_plugin.py`
3. **Delete all old versions** completely
4. Copy the corrected version to plugins directory
5. Restart Veusz completely

### Plugin Doesn't Appear in Menu

**Problem**: Can't find "RPi TKu Telemetry Import" in Data → Import menu

**Solutions**:
1. ✅ Verify file is named: `rpi_tku_import_plugin.py` (underscores only)
2. ✅ Verify it's in correct plugins directory
3. ✅ **Completely restart Veusz** (close all windows)
4. ✅ Delete any old versions that might be conflicting
5. ✅ Make sure you're using **v1.2 (rpi-plugin-corrected.py)**

### Preview Shows "Error generating preview"

**Problem**: Preview section shows an error message

**Solution**:
1. ✅ Make sure you're using **v1.2 (rpi-plugin-corrected.py)**
2. ✅ Delete old version and reinstall corrected version
3. ✅ Verify file encoding (should auto-detect UTF-8, cp1252, or latin-1)

### "Could Not Parse Column Headers"

**Problem**: Plugin can't read the file format

**Solutions**:
1. ✅ Verify file format:
   - Lines 1-8: Header with % prefix
   - Line 9: Comma-separated column names
   - Line 10: Just `%` (empty marker)
   - Line 11+: Data rows
2. ✅ Don't edit .dat files in Excel (corrupts format)
3. ✅ File encoding should be auto-detected

### Datasets Show All NaN Values

**Problem**: Data appears but shows as NaN

**Solutions**:
1. ✅ Check that columns are space-separated in file
2. ✅ Non-numeric values become NaN (expected for text)
3. ✅ Verify data alignment in source file

---

## 💡 Tips & Best Practices

### 1. Always Preview First
Before importing, the preview section shows:
- File name and statistics
- Column count
- Data row count
- Classification of columns by type

### 2. Use Prefixes for Organization
When importing multiple files, use date-based prefixes:
- Prefix: `2025_12_10_`
- Prefix: `2025_12_11_`
- Prefix: `2025_12_12_`

### 3. Organize by Tags
Tags help you find related data:
- Filter by "Voltages" to see all power rails
- Filter by "Amperages" to see all current measurements
- Filter by "StateValues" to see detector status
- Filter by "DateTime" to see timestamp data

### 4. Save Your Work
After creating plots, save the Veusz document:
- **File** → **Save As**
- All datasets and plots are preserved

### 5. Export Plots
Share your analysis:
- **File** → **Export**
- Choose format: PDF, PNG, SVG, etc.

---

## 📚 Next Steps

After your first import:

1. **Create multiple plots** for different data categories
2. **Experiment** with different X-axis choices
3. **Customize** plot appearance (colors, labels, legends)
4. **Annotate** with notes and titles
5. **Export** for reports and presentations

---

## 🔧 What Was Corrected in Version 1.2

**Previous Issues:**
- Incorrect field value retrieval from Veusz API
- String unpacking error in preview method
- Encoding detection issues

**Version 1.2 Fixes:**
- Proper use of `params.field_results.get()` for Veusz API
- Simplified and corrected preview method
- Multiple encoding fallback (UTF-8 → cp1252 → latin-1)
- Removed unnecessary metadata tracking
- Streamlined field definitions

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

---

**Plugin Version**: 1.2 (Corrected)  
**Compatible with**: Veusz 4.2+  
**Created**: 2025-12-10  
**Corrected**: 2025-01-07 (Fixed "too many values" error)

**Ready to use! Download rpi-plugin-corrected.py and follow installation steps above. 📊**
