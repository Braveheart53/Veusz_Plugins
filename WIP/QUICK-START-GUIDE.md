# RPi TKu Telemetry Import Plugin - Quick Start Guide

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

### Step 2: Download and Install

1. Download **`rpi-plugin-enhanced.py`** from this conversation (file above)
2. Rename it to: **`rpi_tku_import_plugin.py`** (remove dashes, use underscores)
3. Copy it to your plugins directory
4. Restart Veusz completely

### Step 3: Verify Installation

1. Open Veusz
2. Click **Data** menu
3. Click **Import** submenu
4. You should see: **"RPi TKu Telemetry Import (Enhanced)"** ✅

---

## 🚀 First Import (5 Minutes)

### Import Your Data

1. In Veusz: **Data** → **Import** → **RPi TKu Telemetry Import (Enhanced)**
2. Click **Browse** and select your `.dat` file
3. Review the preview (shows what will be imported)
4. Leave default options checked:
   - ✓ Create individual plots
   - ✓ Create overlay plots
   - ✓ Convert timestamp
   - ✓ Include header in notes
5. Click **OK**

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
   - **X-axis dataset**: Select `[filename]_UTC Now minus UTC Trigger (sec)`
   - Click the **+** button to add datasets
   - **Y-axis datasets**: Select multiple voltage columns:
     - `[filename]_PS1CH1V`
     - `[filename]_PS1CH2V`
     - `[filename]_PS1CH3V`
     - `[filename]_PS1CH4V`
3. Right-click the graph → **Properties**
4. Add a title: "Power Supply Voltages Over Time"
5. Enable legend: Check "Show legend"

**Result**: You now have a plot showing all power supply voltages overlaid!

### Create Additional Overlay Plots

Repeat the above process for:

**Amperage Plot:**
- Y-axis: All columns ending in 'A'
- Title: "Current Draw Over Time"

**State Values Plot:**
- Y-axis: Detector columns (Det PreAmp, Lock, etc.)
- Title: "System State Values Over Time"

---

## 📋 What Gets Imported

From your `.dat` file, the plugin creates:

### Voltage Datasets (Tagged: "Voltages")
```
[filename]_PS1CH1V
[filename]_PS1CH2V
[filename]_PS1CH3V
[filename]_PS1CH4V
[filename]_PS2CH1V
[filename]_Det +3.3V
[filename]_Det -5V
[filename]_Det +5V
```

### Amperage Datasets (Tagged: "Amperages")
```
[filename]_PS1CH1A
[filename]_PS1CH2A
[filename]_PS1CH3A
[filename]_PS1CH4A
[filename]_PS2CH1A
```

### State/Detector Datasets (Tagged: "StateValues")
```
[filename]_Det PreAmp
[filename]_Det HPA
[filename]_Det AWG
[filename]_Lock
[filename]_MIMIC State
```

### DateTime Dataset (Tagged: "DateTime")
```
[filename]_UTC Now minus UTC Trigger (sec)_DateTime
(Converted to YYYY-MM-DD HH:MM:SS format)
```

### Other Numeric Columns
```
[filename]_TFOM
[filename]_Year
[filename]_DOY
[filename]_AGC
... and more
```

---

## 🎯 Common Tasks

### Import Multiple Files

1. **Data** → **Import** → **RPi TKu Telemetry Import (Enhanced)**
2. Hold **Ctrl** (Windows/Linux) or **Cmd** (Mac) while selecting files
3. Click **Open**
4. All files import with unique dataset names

**Result**: Datasets named like `file1_PS1CH1V`, `file2_PS1CH1V`, etc.

### Add Custom Prefix/Suffix

When importing, use the **Prefix** or **Suffix** fields:

**Example with Date Prefix:**
- Prefix: `2025_12_10_`
- Result: `2025_12_10_Rpi_TKu_file_PS1CH1V`

### Use Converted Datetime for X-Axis

Instead of seconds offset, use the datetime conversion:
- X-axis: Select `[filename]_UTC Now minus UTC Trigger (sec)_DateTime`
- Result: Human-readable date/time labels on X-axis

---

## ⚠️ Troubleshooting

### Plugin Doesn't Appear in Menu

**Problem**: Can't find "RPi TKu Telemetry Import" in Data → Import menu

**Solutions**:
1. ✅ Verify file is named correctly (no dashes, use underscores)
2. ✅ Check file is in correct plugins directory
3. ✅ **Completely restart Veusz** (close all windows)
4. ✅ Try opening Preferences → Plugins to see if it's listed

### "File Not Found" Error

**Problem**: Error when trying to import file

**Solutions**:
1. ✅ Verify .dat file exists at the path you selected
2. ✅ Check file permissions (must be readable)
3. ✅ Try using the file browser to navigate to file

### "Could Not Parse Column Headers"

**Problem**: Plugin can't read the file format

**Solutions**:
1. ✅ Open file in text editor - verify format:
   - Lines 1-8: Header info with % prefix
   - Line 9: Comma-separated column names
   - Line 10: Just `%` (empty marker)
   - Line 11+: Data rows
2. ✅ Ensure file hasn't been edited in Excel (corrupts format)
3. ✅ Check encoding is UTF-8

### Datasets Show All NaN Values

**Problem**: Data appears but shows as NaN

**Solutions**:
1. ✅ Check that columns are space-separated in file
2. ✅ Non-numeric values automatically become NaN (expected for text)
3. ✅ Verify data alignment in source file

### Timestamp Shows "Invalid"

**Problem**: DateTime conversion shows "Invalid" instead of dates

**Solutions**:
1. ✅ Verify file header contains `UTC Trigger Time Stamp`
2. ✅ Check that timestamp value is valid Unix timestamp
3. ✅ Try disabling timestamp conversion in import dialog

---

## 💡 Tips & Best Practices

### 1. Always Preview First
Before importing large files, use the preview to verify:
- Column count matches expected
- File structure is correct
- Data format looks good

### 2. Use Meaningful Prefixes
When importing multiple files, use date-based prefixes:
```
2025_12_10_
2025_12_11_
2025_12_12_
```

### 3. Organize by Tags
Use tags to quickly find related datasets:
- Filter by "Voltages" to see all power rails
- Filter by "Amperages" to see all current draw
- Filter by "StateValues" to see detector status

### 4. Save Your Work
After creating plots, save the Veusz document:
- **File** → **Save As** → Choose location
- Datasets and plots are preserved
- Can reload later for analysis

### 5. Export Plots
Share your analysis:
- **File** → **Export** → Choose format (PDF, PNG, SVG)
- High-quality output for reports

---

## 📚 Next Steps

After completing this quick start:

1. **Experiment**: Try importing different .dat files
2. **Explore**: Create different plot types and layouts
3. **Customize**: Adjust colors, labels, legends
4. **Analyze**: Look for trends and correlations in your data
5. **Document**: Add notes and annotations to plots

For detailed documentation, see the full guides included in the delivery package.

---

## 📞 Need More Help?

- Check the comprehensive **USAGE_GUIDE.md** for detailed workflows
- Review **TECHNICAL_SPECIFICATION.md** for technical details
- See **README.md** for feature overview

---

## ✅ Quick Reference

| Task | Steps |
|------|-------|
| **Install** | Copy to plugins dir → Restart Veusz |
| **Import** | Data → Import → Select file → OK |
| **View Data** | Data → List Datasets |
| **Plot** | Insert → Graph → Select datasets |
| **Overlay** | Add multiple Y-axis datasets to one graph |
| **Export** | File → Export → Choose format |
| **Save** | File → Save As |

---

**Plugin Version**: 1.1 (Enhanced)  
**Compatible with**: Veusz 4.2+  
**Created**: 2025-12-10  

**You're all set! Enjoy analyzing your telemetry data! 📊**
