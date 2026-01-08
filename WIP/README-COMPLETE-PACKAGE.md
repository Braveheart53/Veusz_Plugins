# 📦 Complete Plugin Package - Version 1.3 Enhanced

## Files You Have (Download All Three)

### 1. **Plugin Code** (Required)
- **File**: `rpi-plugin-v1-3.py` [11]
- **Size**: ~15 KB
- **Purpose**: The actual Veusz import plugin
- **Installation**: Rename to `rpi_tku_import_plugin.py` and place in plugins directory

### 2. **Quick Start Guide** (Recommended)
- **File**: `QUICK-START-v1-3.md` [12]
- **Purpose**: Step-by-step installation and usage guide
- **Contains**: 
  - Installation instructions for all OS
  - First import walkthrough
  - Dataset notes interpretation
  - Troubleshooting section
  - Tips and best practices

### 3. **Features Summary** (Reference)
- **File**: `ENHANCED-v1-3-SUMMARY.md` [13]
- **Purpose**: Overview of v1.3 enhancements
- **Contains**:
  - New features detailed
  - Statistical analysis guide
  - Practical application examples
  - Technical improvements list
  - Metadata tracking details

---

## 🎯 30-Second Quick Start

### If you're in a hurry:

1. **Download** `rpi-plugin-v1-3.py` [11]
2. **Rename** to `rpi_tku_import_plugin.py` (remove dashes, use underscores)
3. **Place** in:
   - Windows: `%APPDATA%\Veusz\plugins\`
   - Linux: `~/.veusz/plugins/`
   - Mac: `~/Library/Application Support/Veusz/plugins/`
4. **Restart** Veusz
5. **Go to** Data → Import → Select your .dat file
6. Click **OK**

✅ Done! Your data is imported with full metadata and statistics.

---

## 📊 What You Get

### Automatic Features (No Configuration Needed)

✅ **Intelligent Data Organization**
- Automatic tagging (Voltages, Amperages, StateValues, DateTime)
- Original column names preserved
- Consistent naming with filename prefix

✅ **Statistical Analysis**
- Min, Max, Mean calculated automatically
- Standard deviation for stability assessment
- NaN/missing value counting
- Displayed in dataset Notes

✅ **Quality Metadata**
- File header context with each dataset
- Import timestamp and source tracking
- Complete audit trail for reproducibility

✅ **Smart Timestamp Conversion**
- Converts raw MJD seconds to YYYY-MM-DD HH:MM:SS
- Creates searchable datetime dataset
- Preserves original timestamp dataset too

---

## 💡 Key Features Explained

### Feature 1: Dataset Tags
```
After import, datasets are tagged:
- "Voltages" → All columns ending in V
- "Amperages" → All columns ending in A  
- "StateValues" → Detector status columns
- "DateTime" → Time-related columns

Benefit: Quickly find related datasets using filter
```

### Feature 2: Dataset Notes with Statistics
```
When you open a dataset's Notes tab:

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

Benefit: See data quality and ranges at a glance
```

### Feature 3: File Header Context
```
Every dataset's notes include:
- File header lines
- UTC trigger timestamp
- Import metadata

Benefit: Complete context without re-opening file
```

### Feature 4: Configurable Import
```
Three toggles in the import dialog:
□ Convert timestamp (default: ✓)
□ Store statistics (default: ✓)
□ Include header in notes (default: ✓)

Benefit: Optimize for your use case
```

---

## 🔍 Understanding Dataset Notes

### Example: Voltage Channel Note

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
  Detector Element: Test
```

**How to read it:**
- **Original column**: Where this came from in the file
- **Category**: Type of measurement
- **Valid points**: How many measurements (1024 = complete)
- **Missing values**: Data gaps (0 = perfect)
- **Min/Max**: Expected voltage range (11.85-12.15V)
- **Mean**: Average voltage (12.00V = nominal)
- **Std Dev**: Voltage stability (0.087V = stable)

### Example: State Value Note

```
Original column: Det PreAmp
Category: State
Tags: StateValues

Statistics:
  Valid points: 1022
  Missing values: 2
  Min: 0.0
  Max: 1.0
  Std Dev: 0.445

File Header Information:
  [File context...]
```

**How to read it:**
- **Valid points**: 1022/1024 (99.8% coverage)
- **Missing values**: 2 gaps in data (0.2%)
- **Min/Max**: Binary state (0=off, 1=on)
- **Std Dev**: 0.445 indicates frequent state changes

---

## 🛠️ Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Plugin doesn't appear in menu | Verify filename is `rpi_tku_import_plugin.py` (underscores), restart Veusz |
| "too many values to unpack" error | You're using old version - delete old files, install v1.3 |
| Preview shows error | Use v1.3 (`rpi-plugin-v1-3.py`), delete old versions |
| Statistics missing from notes | Check "Store statistics" option is checked during import |
| Header info not in notes | Check "Include header in notes" option is checked |
| Dataset shows all NaN | File format issue - verify file structure |

---

## 📈 What Happens During Import

```
Your .dat file → [Plugin Processing] → Veusz Datasets

Processing steps:
1. ✓ Read file with automatic encoding detection
2. ✓ Parse header lines to get metadata
3. ✓ Extract column names from CSV header
4. ✓ Parse all data values (space-separated)
5. ✓ Categorize each column (voltage/amperage/state/etc)
6. ✓ Convert timestamps to readable format
7. ✓ Calculate statistics (min/max/mean/std)
8. ✓ Create formatted notes with all context
9. ✓ Tag datasets for organization
10. ✓ Import into Veusz as searchable datasets

Result: Tagged, documented, statistically analyzed datasets
ready for plotting and analysis
```

---

## 🎓 Common Analysis Workflows

### Workflow 1: Quick Data Quality Check
```
1. Import file (all defaults)
2. Data → List Datasets
3. Spot check a few datasets' Notes tabs
4. Look for:
   - Missing values count
   - Reasonable min/max values
   - Standard deviation patterns
5. Note any datasets with issues
```

### Workflow 2: Multi-File Comparison
```
1. Import first file with prefix "2025_01_07_"
2. Import second file with prefix "2025_01_08_"
3. For same column in both files:
   - Compare statistics in dataset notes
   - Look for trends or changes
   - Document differences
```

### Workflow 3: Create Analysis Report
```
1. Import data (all defaults)
2. For each category (voltages, amperages, etc):
   - Create overlay plot
   - Add title and legend
   - Export as PNG/PDF
3. Document with:
   - Dataset notes (copy from Notes tab)
   - Statistics from notes
   - Export plots
4. Create comprehensive report
```

---

## 🔧 System Requirements

**Minimum:**
- Veusz 4.2 or later
- Python 3.6+
- NumPy (usually included with Veusz)

**Recommended:**
- Veusz 4.3+
- 2GB RAM (for large telemetry files)
- 100MB disk space

**File Format:**
- RPi TKu .dat files
- UTF-8, cp1252, or latin-1 encoding
- Standard space-separated format

---

## 📞 Quick Reference Card

```
┌─ INSTALLATION ─────────────────────────────┐
│ 1. Download: rpi-plugin-v1-3.py [11]       │
│ 2. Rename to: rpi_tku_import_plugin.py     │
│ 3. Place in: Veusz plugins directory       │
│ 4. Restart Veusz                           │
└────────────────────────────────────────────┘

┌─ FIRST IMPORT ──────────────────────────────┐
│ 1. Data → Import                            │
│ 2. Select: RPi TKu Telemetry Import        │
│ 3. Browse to your .dat file                 │
│ 4. Leave all options checked (default)      │
│ 5. Click OK                                 │
└─────────────────────────────────────────────┘

┌─ VIEW STATISTICS ───────────────────────────┐
│ 1. Data → List Datasets                    │
│ 2. Select any dataset                       │
│ 3. Click "Notes" tab at bottom              │
│ 4. Read formatted statistics and metadata   │
└─────────────────────────────────────────────┘

┌─ CREATE PLOTS ──────────────────────────────┐
│ 1. Insert → Graph                           │
│ 2. Select X-axis dataset (time usually)     │
│ 3. Click + to add Y-axis datasets           │
│ 4. Select related columns (all voltages, etc) │
│ 5. Right-click → Properties to customize    │
└─────────────────────────────────────────────┘
```

---

## ✅ Success Checklist

After installation, you should be able to:

- [ ] See plugin in Data → Import menu
- [ ] Select a .dat file and see preview
- [ ] Import completes with no errors
- [ ] Datasets appear in Data → List Datasets
- [ ] Each dataset has appropriate tags
- [ ] Dataset Notes tab shows statistics
- [ ] Notes include min, max, mean, std dev
- [ ] File header context appears in notes
- [ ] Can create plots from imported data
- [ ] Export plots as PNG/PDF

If all checked: ✅ You're good to go!

---

## 📚 Documentation Files Summary

| File | Purpose | When to Use |
|------|---------|-----------|
| `rpi-plugin-v1-3.py` [11] | Actual plugin code | Installation |
| `QUICK-START-v1-3.md` [12] | Complete guide | Getting started |
| `ENHANCED-v1-3-SUMMARY.md` [13] | Feature details | Learning features |
| This file | Quick reference | Daily usage |

---

## 🎉 Ready to Begin?

### Start Here:
1. Download **all three files** [11][12][13]
2. Follow **30-Second Quick Start** above (or detailed guide [12])
3. Import your first .dat file
4. Check dataset Notes to see statistics
5. Create your first plot
6. Export your analysis

**Questions?** See the troubleshooting section in QUICK-START-v1-3.md [12]

---

**You have everything you need for professional RPi TKu telemetry analysis!** 📊✨

Version 1.3 | Enhanced Production | Ready to Use
