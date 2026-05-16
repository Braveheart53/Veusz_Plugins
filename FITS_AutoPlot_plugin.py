# -*- coding: utf-8 -*-
"""
=============================================================================
FITS_AutoPlot_plugin.py
-----------------------------------------------------------------------------
# %% Header Info

Veusz Tools plugin equivalent of FITS_AutoPlot.py.  Drop this file into
your Veusz plugins folder (or load it via
``Edit > Preferences > Plugins > Add``) and the entry

    Tools -> NRAO / FitsAutoPlot -> FITS AutoPlot (Batch)

will appear.  Selecting it opens the same Touchstone-style qtpy GUI as the
standalone script and, when the user clicks "Process Files", pours every
column dataset and plot page into the current Veusz document.

# %%% Author Information
@author: William W. Wallace
Author Email: wwallace@nrao.edu
Author Secondary Email: naval.antennas@gmail.com
Author Business Phone: +1 (304) 456-2216

# %%% Revisions
Utilizing Semantic Schema as External Release.Internal Release.Working version

# %%%% 0.0.1: Initial plugin equivalent of FITS_AutoPlot.py
Date: 2026-05-16
# %%%% 0.0.2: Added "Generate MJD->date strings" checkbox to the modal
#             dialog and an ``emit_datestr`` boolean field so the same
#             option is available from the Veusz Tools menu.
Date: 2026-05-16
# %%%% 0.0.3: NaN-preserving emission policy (inherits push_to_veusz from
#             FITS_AutoPlot.py): numeric NaN floats are kept verbatim in
#             Veusz numeric datasets; non-finite MJDs become the sentinel
#             string ``"NaN"`` in the date-string text datasets so row
#             counts always match their numeric companions.
Date: 2026-05-16
# %%%% 0.0.4: FITS-unit-warning suppression.  The plugin already inherits
#             register_nrao_fits_units() and the suppress_fits_unit_warnings()
#             context manager via FITSProcessor (imported from
#             FITS_AutoPlot.py).  As a belt-and-suspenders measure we
#             explicitly call register_nrao_fits_units() at plugin module
#             load and wrap the entire apply() FITS-reading loop in the
#             suppression context manager so the Veusz log stays clean
#             during batch runs of 1PPS-delta files.
Date: 2026-05-16
# %%%%% Function Descriptions
        FITSAutoPlotPlugin: Veusz ToolsPlugin subclass with menu entry,
            description, field definitions (file list, backend, threads,
            RSS spill, theme) and the apply() entry-point.
        _PluginInterfaceAdapter: tiny shim that lets the same push_to_veusz
            implementation (from FITS_AutoPlot.py) work against either
            ``veusz.embed.Embedded`` (standalone) or the document
            ``CommandInterface`` (plugin context) by delegating common
            methods to the supplied interface.
# %%%%% Variable Descriptions
        MAX_THREADS: top-of-file knob for the worker thread pool size,
            mirrored from the standalone script.
# %%%%% More Info
        Veusz plugins receive a ``CommandInterface`` (Veusz 4.x) or a
        ``Embedded``-like interface (Veusz 3.4); both expose the same
        SetData / SetData2D / TagDatasets / ImportFileFITS / Root.Add()
        surface used by ``FITS_AutoPlot.push_to_veusz``, so the plugin can
        reuse the standalone implementation directly.

        The plugin shows the Touchstone-style GUI in modal form so that the
        user can pick a theme, threads and backend without leaving the
        Veusz session.  Once the user closes the dialog the plugin returns
        and the new datasets/pages are visible immediately in the parent
        Veusz window.
=============================================================================
"""
from __future__ import annotations

import os
import sys
import traceback
from typing import Any, Dict, List

# Make sibling files importable when Veusz loads the plugin from a path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import veusz.plugins as vzp

# Reuse the standalone implementation
from FITS_AutoPlot import (                       # noqa: E402
    MAX_THREADS, DEFAULT_RSS_HIGH_WATER_MB,
    FITSProcessor, push_to_veusz,
)
from _autoplot_common import (                    # noqa: E402
    QApplication, QFileDialog, QMessageBox,
    QSpinBox, QComboBox, QCheckBox, QFormLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QProgressBar, QTextEdit,
    apply_theme, MemoryAwareCache, MemoryMonitorConfig, MemoryMonitor,
    run_in_threadpool,
    register_nrao_fits_units, suppress_fits_unit_warnings,
)

# Idempotent: ensures the NRAO custom FITS unit aliases ('none',
# 'NanoSeconds') are registered with astropy.units even if this plugin
# happens to be loaded before FITS_AutoPlot.py would otherwise run its
# module-level registration call.
register_nrao_fits_units()
# qtpy's QDialog
try:
    from qtpy.QtWidgets import QDialog
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import QDialog


# ============================================================================
# A modal qtpy dialog mirroring the standalone GUI layout
# ============================================================================
class _PluginBatchDialog(QDialog):
    """Modal version of the AutoPlot main window for in-plugin use."""

    def __init__(self, parent=None, default_mode: str = "dark") -> None:
        super().__init__(parent)
        self.setWindowTitle("FITS AutoPlot - Veusz Plugin")
        self.resize(900, 700)
        self.selected_files: List[str] = []
        self._theme_mode = default_mode

        root = QVBoxLayout(self)

        # Theme toggle row (textual menu would require a QMainWindow)
        trow = QHBoxLayout()
        trow.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Mode", "Light Mode"])
        self.theme_combo.setCurrentIndex(0 if default_mode == "dark" else 1)
        self.theme_combo.currentIndexChanged.connect(self._theme_changed)
        trow.addWidget(self.theme_combo)
        trow.addStretch()
        root.addLayout(trow)

        # File selection
        root.addWidget(QLabel("Input files:"))
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(160)
        root.addWidget(self.file_list)
        brow = QHBoxLayout()
        b1 = QPushButton("Browse...")
        b1.clicked.connect(self._browse)
        brow.addWidget(b1)
        b2 = QPushButton("Clear")
        b2.clicked.connect(self._clear)
        brow.addWidget(b2)
        root.addLayout(brow)

        # Options
        form = QFormLayout()
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["both (Veusz + astropy)",
                                     "veusz (native FITS import)",
                                     "astropy"])
        form.addRow("Import backend:", self.backend_combo)
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, max(1, (os.cpu_count() or 4) * 2))
        self.thread_spin.setValue(MAX_THREADS)
        form.addRow("Worker threads:", self.thread_spin)
        self.rss_spin = QSpinBox()
        self.rss_spin.setRange(128, 65536)
        self.rss_spin.setSingleStep(128)
        self.rss_spin.setValue(DEFAULT_RSS_HIGH_WATER_MB)
        form.addRow("RSS spill threshold (MiB):", self.rss_spin)
        root.addLayout(form)

        self.datestr_cb = QCheckBox(
            "Generate MJD -> date strings (YYYY-MM-DD_HH:MM:SS) datasets"
        )
        self.datestr_cb.setChecked(False)
        root.addWidget(self.datestr_cb)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(140)
        root.addWidget(self.log)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        # Action buttons
        arow = QHBoxLayout()
        self.process_btn = QPushButton("Process Files")
        self.process_btn.clicked.connect(self.accept)   # close dialog -> plugin reads selection
        arow.addWidget(self.process_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        arow.addWidget(self.cancel_btn)
        root.addLayout(arow)

        apply_theme(QApplication.instance(), default_mode)

    # ----- helpers ---------------------------------------------------------
    def _theme_changed(self, idx: int) -> None:
        mode = "dark" if idx == 0 else "light"
        self._theme_mode = mode
        apply_theme(QApplication.instance(), mode)

    def _browse(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select FITS files", "",
            "FITS files (*.fits *.fit *.fits.gz *.fit.gz);;All files (*)"
        )
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
        self.file_list.clear()
        for p in self.selected_files:
            self.file_list.addItem(os.path.basename(p))

    def _clear(self) -> None:
        self.selected_files.clear()
        self.file_list.clear()

    def append_log(self, msg: str) -> None:
        self.log.append(msg)


# ============================================================================
# THE PLUGIN
# ============================================================================
class FITSAutoPlotPlugin(vzp.ToolsPlugin):
    """Veusz Tools plugin: batch process NRAO FITS files into the current document."""

    menu = ("NRAO / FitsAutoPlot", "FITS AutoPlot (Batch)")
    name = "FITS AutoPlot"
    description_short = "Batch import NRAO FITS files (column oriented)"
    description_full = (
        "Open a Touchstone-style GUI to select one or more FITS files "
        "(compressed .gz allowed), choose backend (Veusz native, astropy, "
        "or both), threading and RSS spill threshold, then load all columns "
        "as Veusz datasets tagged by filename and raw/sorted, with a plot "
        "page per HDU."
    )

    def __init__(self) -> None:
        self.fields = [
            vzp.FieldText("default_theme",
                          descr="Default theme (dark/light)",
                          default="dark"),
            vzp.FieldInt("max_threads",
                         descr="Maximum worker threads",
                         default=MAX_THREADS, minval=1, maxval=128),
            vzp.FieldInt("rss_mb",
                         descr="RSS spill threshold (MiB)",
                         default=DEFAULT_RSS_HIGH_WATER_MB,
                         minval=128, maxval=65536),
            vzp.FieldText("preselected_files",
                          descr="Optional: ;-separated FITS file paths "
                                "(leave blank to pick interactively)",
                          default=""),
            vzp.FieldBool("emit_datestr",
                          descr="Also create MJD -> date-string datasets "
                                "(YYYY-MM-DD_HH:MM:SS)",
                          default=False),
        ]

    # ------------------------------------------------------------------
    def apply(self, interface, fields):
        """Plugin entry point.  ``interface`` is the document command API."""
        try:
            return self._apply(interface, fields)
        except Exception as exc:
            raise vzp.ToolsPluginException(
                "FITS AutoPlot plugin failed: %s\n%s" %
                (exc, traceback.format_exc())
            )

    def _apply(self, interface, fields):
        app = QApplication.instance() or QApplication(sys.argv)
        mode = "dark" if (fields.get("default_theme") or "dark").lower().startswith("d") else "light"
        dlg = _PluginBatchDialog(default_mode=mode)

        # Honour pre-seeded file list
        pre = (fields.get("preselected_files") or "").strip()
        if pre:
            for p in [x.strip() for x in pre.split(";") if x.strip()]:
                if os.path.isfile(p):
                    dlg.selected_files.append(p)
            for p in dlg.selected_files:
                dlg.file_list.addItem(os.path.basename(p))
        dlg.thread_spin.setValue(int(fields.get("max_threads") or MAX_THREADS))
        dlg.rss_spin.setValue(int(fields.get("rss_mb") or DEFAULT_RSS_HIGH_WATER_MB))
        dlg.datestr_cb.setChecked(bool(fields.get("emit_datestr") or False))

        if dlg.exec_() != QDialog.Accepted:
            return
        if not dlg.selected_files:
            QMessageBox.information(None, "FITS AutoPlot",
                                    "No files selected -- aborting.")
            return

        backend = ["both", "veusz", "astropy"][dlg.backend_combo.currentIndex()]
        cache = MemoryAwareCache(MemoryMonitorConfig(
            rss_high_water_mb=int(dlg.rss_spin.value())
        ))
        mon = MemoryMonitor(cache, callback=lambda r: dlg.append_log(
            "RSS over high-water mark (%.1f MiB) -- spilling." % r))
        mon.start()

        proc = FITSProcessor(backend, cache)
        # Sequentially run-in-threadpool inside this plugin call: we use
        # threads (not processes) so the plugin remains within the Veusz
        # interpreter and can write to ``interface`` directly afterwards.
        work = [(p, proc.read, (p,)) for p in dlg.selected_files]
        dlg.progress.setVisible(True)
        dlg.progress.setRange(0, len(work))
        progress_state = {"done": 0}

        def _cb(done, total, key):
            progress_state["done"] = done
            dlg.progress.setValue(done)
            dlg.append_log("read [%d/%d] %s" % (done, total, os.path.basename(key)))
            app.processEvents()

        # Belt-and-suspenders: suppress NRAO FITS unit warnings around the
        # entire batch read + push.  FITSProcessor already wraps fits.open
        # / QTable.read internally, but this outer context ensures that any
        # downstream astropy code paths (e.g. push_to_veusz fallbacks) also
        # stay quiet during the Veusz batch run.
        with suppress_fits_unit_warnings():
            results = run_in_threadpool(work,
                                        max_workers=int(dlg.thread_spin.value()),
                                        progress_cb=_cb)
            emit_datestr = bool(dlg.datestr_cb.isChecked())
            dlg.append_log("Pushing datasets into Veusz document...")
            for path, data in results.items():
                if isinstance(data, Exception):
                    dlg.append_log("  ERROR %s: %s" % (path, data))
                    continue
                push_to_veusz(interface, path, data, backend,
                              log_cb=dlg.append_log,
                              emit_datestr=emit_datestr)
                app.processEvents()
        dlg.append_log("Done.")
        mon.stop()
        cache.cleanup()


# ============================================================================
# REGISTER WITH VEUSZ
# ============================================================================
vzp.toolspluginregistry.append(FITSAutoPlotPlugin)
