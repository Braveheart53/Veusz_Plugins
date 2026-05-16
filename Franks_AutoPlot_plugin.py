# -*- coding: utf-8 -*-
"""
=============================================================================
Franks_AutoPlot_plugin.py
-----------------------------------------------------------------------------
# %% Header Info

Veusz Tools plugin equivalent of Franks_AutoPlot.py.  Adds the menu entry

    Tools -> NRAO / FitsAutoPlot -> Franks AutoPlot (Batch)

to the active Veusz instance.  Invoking it opens a Touchstone-style qtpy
dialog identical in shape to the standalone Franks_AutoPlot.py window
(file list, thread count, RSS spill threshold, theme toggle, log area,
progress bar) and on accept pours every parsed column dataset and plot
page into the *current* document.

# %%% Author Information
@author: William W. Wallace
Author Email: wwallace@nrao.edu
Author Secondary Email: naval.antennas@gmail.com
Author Business Phone: +1 (304) 456-2216

# %%% Revisions
Utilizing Semantic Schema as External Release.Internal Release.Working version

# %%%% 0.0.1: Initial plugin equivalent of Franks_AutoPlot.py
Date: 2026-05-16
# %%%%% Function Descriptions
        FranksAutoPlotPlugin: Veusz ToolsPlugin subclass providing the menu
            entry, fields (max_threads, rss_mb, default_theme, preseed) and
            the apply() entry point.
        _PluginBatchDialog: modal qtpy dialog mirroring the standalone
            main window without a menu bar (plugin dialogs cannot host a
            QMainWindow menu, so dark/light is offered as a combo box).
# %%%%% Variable Descriptions
        MAX_THREADS / DEFAULT_RSS_HIGH_WATER_MB: imported from
            Franks_AutoPlot.py so all four deliverables share the same
            top-of-file knobs.
# %%%%% More Info
        Because the Franks data files are pure ASCII, no equivalent of
        Veusz's native FITS importer is offered; the plugin always parses
        with numpy and produces both raw and sorted Veusz datasets, both
        tagged with the file's base name plus 'raw' / 'sorted'.
=============================================================================
"""
from __future__ import annotations

import os
import sys
import traceback
from typing import Any, Dict, List

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import veusz.plugins as vzp

from Franks_AutoPlot import (                       # noqa: E402
    MAX_THREADS, DEFAULT_RSS_HIGH_WATER_MB,
    parse_franks_file, push_franks_to_veusz,
)
from _autoplot_common import (                      # noqa: E402
    QApplication, QFileDialog, QMessageBox,
    QSpinBox, QComboBox, QCheckBox, QFormLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QProgressBar, QTextEdit,
    apply_theme, MemoryAwareCache, MemoryMonitorConfig, MemoryMonitor,
    run_in_threadpool,
)
try:
    from qtpy.QtWidgets import QDialog
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import QDialog


# ============================================================================
# Modal dialog (mirror of the standalone GUI)
# ============================================================================
class _PluginBatchDialog(QDialog):
    """Modal qtpy dialog used by the plugin entry point."""

    def __init__(self, parent=None, default_mode: str = "dark") -> None:
        super().__init__(parent)
        self.setWindowTitle("Franks AutoPlot - Veusz Plugin")
        self.resize(900, 700)
        self.selected_files: List[str] = []
        self._theme_mode = default_mode

        root = QVBoxLayout(self)

        trow = QHBoxLayout()
        trow.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Mode", "Light Mode"])
        self.theme_combo.setCurrentIndex(0 if default_mode == "dark" else 1)
        self.theme_combo.currentIndexChanged.connect(self._theme_changed)
        trow.addWidget(self.theme_combo)
        trow.addStretch()
        root.addLayout(trow)

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

        form = QFormLayout()
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

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(140)
        root.addWidget(self.log)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        arow = QHBoxLayout()
        self.process_btn = QPushButton("Process Files")
        self.process_btn.clicked.connect(self.accept)
        arow.addWidget(self.process_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        arow.addWidget(self.cancel_btn)
        root.addLayout(arow)

        apply_theme(QApplication.instance(), default_mode)

    def _theme_changed(self, idx: int) -> None:
        mode = "dark" if idx == 0 else "light"
        self._theme_mode = mode
        apply_theme(QApplication.instance(), mode)

    def _browse(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Franks data files", "",
            "Franks files (*.t00new *.dat *.bak* *.OrigBack* *.back);;All files (*)"
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
class FranksAutoPlotPlugin(vzp.ToolsPlugin):
    """Veusz Tools plugin: batch process FranksProcessed files into the current document."""

    menu = ("NRAO / FitsAutoPlot", "Franks AutoPlot (Batch)")
    name = "Franks AutoPlot"
    description_short = "Batch import FranksProcessed ASCII files (column oriented)"
    description_full = (
        "Open a Touchstone-style GUI to select one or more FranksProcessed "
        "files (*.t00new, time_gbt.dat, and their .bak variants), choose "
        "threading and RSS spill threshold, then load all columns as Veusz "
        "datasets tagged by filename and raw/sorted, with a single plot "
        "page per file showing each numeric column versus MJD."
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
                          descr="Optional: ;-separated file paths "
                                "(leave blank to pick interactively)",
                          default=""),
        ]

    # ------------------------------------------------------------------
    def apply(self, interface, fields):
        try:
            return self._apply(interface, fields)
        except Exception as exc:
            raise vzp.ToolsPluginException(
                "Franks AutoPlot plugin failed: %s\n%s" %
                (exc, traceback.format_exc())
            )

    def _apply(self, interface, fields):
        app = QApplication.instance() or QApplication(sys.argv)
        mode = "dark" if (fields.get("default_theme") or "dark").lower().startswith("d") else "light"
        dlg = _PluginBatchDialog(default_mode=mode)

        pre = (fields.get("preselected_files") or "").strip()
        if pre:
            for p in [x.strip() for x in pre.split(";") if x.strip()]:
                if os.path.isfile(p):
                    dlg.selected_files.append(p)
            for p in dlg.selected_files:
                dlg.file_list.addItem(os.path.basename(p))
        dlg.thread_spin.setValue(int(fields.get("max_threads") or MAX_THREADS))
        dlg.rss_spin.setValue(int(fields.get("rss_mb") or DEFAULT_RSS_HIGH_WATER_MB))

        if dlg.exec_() != QDialog.Accepted:
            return
        if not dlg.selected_files:
            QMessageBox.information(None, "Franks AutoPlot",
                                    "No files selected -- aborting.")
            return

        cache = MemoryAwareCache(MemoryMonitorConfig(
            rss_high_water_mb=int(dlg.rss_spin.value())
        ))
        mon = MemoryMonitor(cache, callback=lambda r: dlg.append_log(
            "RSS over high-water mark (%.1f MiB) -- spilling." % r))
        mon.start()

        work = [(p, parse_franks_file, (p, cache)) for p in dlg.selected_files]
        dlg.progress.setVisible(True)
        dlg.progress.setRange(0, len(work))

        def _cb(done, total, key):
            dlg.progress.setValue(done)
            dlg.append_log("parsed [%d/%d] %s" % (done, total, os.path.basename(key)))
            app.processEvents()

        results = run_in_threadpool(work,
                                    max_workers=int(dlg.thread_spin.value()),
                                    progress_cb=_cb)
        dlg.append_log("Pushing datasets into Veusz document...")
        for path, data in results.items():
            if isinstance(data, Exception):
                dlg.append_log("  ERROR %s: %s" % (path, data))
                continue
            push_franks_to_veusz(interface, data, log_cb=dlg.append_log)
            app.processEvents()
        dlg.append_log("Done.")
        mon.stop()
        cache.cleanup()


# ============================================================================
# REGISTER
# ============================================================================
vzp.toolspluginregistry.append(FranksAutoPlotPlugin)
