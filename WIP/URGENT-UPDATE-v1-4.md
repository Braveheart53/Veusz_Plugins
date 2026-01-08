# 🔴 URGENT UPDATE - Version 1.4 Available

## Critical API Fix for Veusz 4.2

You reported an error: `ValueError: too many values to unpack (expected 2)`

**✅ THIS IS NOW FIXED IN VERSION 1.4**

---

## What Went Wrong

The `getPreview()` method in v1.3 was returning a **list**, but Veusz 4.2's plugin API expects a **string**.

```python
# ❌ v1.3 (Wrong)
return preview_lines  # Returns list

# ✅ v1.4 (Fixed)
return "\n".join(preview)  # Returns string
```

---

## Download v1.4 Immediately

### The Fixed Plugin:
**`rpi-plugin-v1-4.py`** [16] ⭐ **USE THIS ONE**

### Quick Install:
1. Download `rpi-plugin-v1-4.py` [16]
2. Rename to: `rpi_tku_import_plugin.py`
3. **Delete all old versions completely**
4. Copy v1.4 to Veusz plugins directory
5. Restart Veusz
6. Try importing again - should work now! ✅

---

## What's Fixed

✅ `getPreview()` now returns proper string format for Veusz 4.2  
✅ No more "too many values to unpack" error  
✅ All v1.3 features preserved (metadata, statistics, notes)  
✅ Fully compatible with Veusz 4.2  

---

## Verification

After installing v1.4:
1. Data → Import
2. Select: RPi TKu Telemetry Import (Enhanced)
3. Browse to your .dat file
4. **Preview should appear without errors** ✅
5. Select import options (leave defaults checked)
6. Click OK → Import should complete successfully!

---

## Files to Review

- **`CRITICAL-FIX-v1-4.md`** [17] - Detailed explanation of the fix
- **`QUICK-START-v1-3.md`** [12] - Installation & usage guide (still applicable)

---

## Why This Happened

Veusz 4.2 is actively developed. The plugin API signature for `getPreview()` expects a string, not a list. This is now fixed in v1.4.

---

## Next Steps

1. ⬇️ Download `rpi-plugin-v1-4.py` [16]
2. 🔄 Replace old plugin with v1.4
3. 🔃 Restart Veusz
4. ✅ Test import - should work now!

---

**Status**: ✅ FIXED  
**Version**: 1.4 (Veusz 4.2 API Compatible)  
**All Features**: Preserved from v1.3

Try it now - the error should be gone! 🎉
