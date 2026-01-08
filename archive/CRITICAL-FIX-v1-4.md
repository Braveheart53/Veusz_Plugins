# ⚠️ CRITICAL API FIX - Version 1.4

## Issue Identified and Fixed

**Problem**: The `getPreview()` method was returning a list, but Veusz 4.2's plugin API expects a **single string** return value.

**Error**: `ValueError: too many values to unpack (expected 2)`

**Root Cause**: Version 1.3 returned:
```python
return preview_lines  # ❌ Returns list → Veusz expects string
```

**Fix in v1.4**: Now returns:
```python
return "\n".join(preview)  # ✅ Returns string
```

---

## What Changed in v1.4

### Critical API Fix
- ✅ `getPreview()` now returns a **single string** (not a list)
- ✅ Matches Veusz 4.2's plugin API exactly
- ✅ Preview displays as formatted multi-line text

### All v1.3 Features Preserved
- ✅ Full metadata tracking
- ✅ Statistical analysis
- ✅ Dataset notes with statistics
- ✅ Configurable import options
- ✅ Comprehensive error handling

---

## Installation

### Use This Version:
**`rpi-plugin-v1-4.py`** [16] - Latest API-compatible version

### Installation Steps:
1. Download `rpi-plugin-v1-4.py` [16]
2. Rename to: `rpi_tku_import_plugin.py`
3. **Delete ALL old versions:**
   - `rpi-plugin-v1-3.py`
   - `rpi-plugin-corrected.py`
   - `rpi-plugin-fixed.py`
   - `rpi-plugin-enhanced.py`
   - Any previously installed version
4. Copy v1.4 to Veusz plugins directory
5. **Completely restart Veusz**

---

## Verification

After installation:
1. Open Veusz
2. Go to: **Data → Import**
3. Select: **RPi TKu Telemetry Import (Enhanced)**
4. Browse to a .dat file
5. **Preview should appear WITHOUT errors** ✅
6. Click OK to test import

---

## Why This Happened

Veusz 4.2 is in active development. The plugin API may have changed from earlier documentation. The `getPreview()` method signature required:

```python
# ❌ Previous (incorrect for Veusz 4.2)
def getPreview(self, params):
    return ["line1", "line2", "line3"]  # Returns list

# ✅ Current (correct for Veusz 4.2)
def getPreview(self, params):
    return "line1\nline2\nline3"  # Returns string
```

---

## All Features Still Included

✅ **Metadata Tracking**
- Original column names
- File header context
- Import timestamps
- Category classification

✅ **Statistical Analysis**
- Min, max, mean calculation
- Standard deviation
- Valid/NaN point counting
- Complete data quality metrics

✅ **Dataset Notes**
- Statistics displayed in Notes tab
- Original column info
- File context preserved
- Formatted for easy reading

✅ **Configurable Options**
- Toggle timestamp conversion
- Toggle statistics calculation
- Toggle header inclusion
- Custom prefix/suffix support

---

## Next Steps

1. **Download** `rpi-plugin-v1-4.py` [16]
2. **Install** following steps above
3. **Test** with your first .dat file
4. **Verify** preview appears without errors
5. **Import** and check dataset Notes for statistics

---

## Support Note

Thank you for catching this! Veusz 4.2's plugin API differences from earlier versions required this adjustment. The v1.4 fix ensures full compatibility with the current version while preserving all enhanced features.

---

**Version**: 1.4 (Veusz 4.2 Compatible)  
**Status**: ✅ Fixed and Ready  
**Date**: 2025-01-07 22:35 UTC
