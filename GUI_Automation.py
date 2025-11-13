"""
GUI for Buckeling Automation
Provides table-based interface for batch processing depth and surface weight inputs
"""
from __future__ import annotations

import csv
import io
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List
import pandas as pd

from Automation import run_automation_batch


INPUT_COLUMNS = (
    ("depth", "Depth (ft)"),
    ("surface_weight", "Surface Weight (lbs)"),
)


def _normalize_header(value: str) -> str:
    """Normalize header strings for clipboard matching."""
    return value.lower().strip().replace(" ", "_").replace("(", "").replace(")", "")


class BuckelingAutomationGUI:
    """GUI for automating buckeling calculations with depth and weight inputs"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Buckeling Automation")
        self.root.geometry("900x600")
        
        # Result storage
        self.result_rows: List[Dict[str, Any]] = []
        self.result_columns: List[str] = []
        
        # Threading
        self.worker_thread: threading.Thread | None = None
        self.is_running = False
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")
        
        self._build_layout()
        
    def _build_layout(self):
        """Build the GUI layout"""
        # Create main container with paned window
        container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Input frame (left side)
        input_frame = ttk.Frame(container, padding=10)
        result_frame = ttk.Frame(container, padding=10)
        container.add(input_frame, weight=1)
        container.add(result_frame, weight=2)
        
        # Input table
        ttk.Label(input_frame, text="Input Rows").pack(anchor=tk.W)
        self.input_tree = ttk.Treeview(
            input_frame,
            columns=[col for col, _ in INPUT_COLUMNS],
            show="headings",
            selectmode="extended",
        )
        for col, heading in INPUT_COLUMNS:
            self.input_tree.heading(col, text=heading)
            self.input_tree.column(col, width=150, anchor=tk.CENTER)
        self.input_tree.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        self.input_tree.bind("<Double-1>", self._edit_input_cell)
        self.input_tree.bind("<Delete>", self._delete_selected_rows)
        
        # Button row for input management
        button_row = ttk.Frame(input_frame)
        button_row.pack(fill=tk.X, pady=5)
        self.btn_add = ttk.Button(button_row, text="Add Row", command=self._add_input_row)
        self.btn_add.pack(side=tk.LEFT)
        self.btn_remove = ttk.Button(button_row, text="Remove Selected", command=self._remove_selected)
        self.btn_remove.pack(side=tk.LEFT, padx=(5, 0))
        self.btn_paste = ttk.Button(button_row, text="Paste Rows", command=self._paste_rows)
        self.btn_paste.pack(side=tk.LEFT, padx=(5, 0))
        
        # Control buttons
        control_row = ttk.Frame(input_frame)
        control_row.pack(fill=tk.X, pady=(10, 0))
        self.btn_run = ttk.Button(control_row, text="Run Automation", command=self._run_automation)
        self.btn_run.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(control_row, text="Stop", command=self._stop_automation, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status label
        ttk.Label(input_frame, textvariable=self.status_var).pack(anchor=tk.W, pady=(10, 0))
        
        # Results frame (right side)
        ttk.Label(result_frame, text="Results").pack(anchor=tk.W)
        
        # Results table
        self.result_tree = ttk.Treeview(result_frame, columns=(), show="headings", selectmode="browse")
        self.result_tree.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        # Copy results button
        copy_row = ttk.Frame(result_frame)
        copy_row.pack(fill=tk.X)
        self.btn_copy = ttk.Button(copy_row, text="Copy Results", command=self._copy_results)
        self.btn_copy.pack(side=tk.LEFT)
        
    def _add_input_row(self):
        """Add a new empty row to the input table"""
        self.input_tree.insert("", tk.END, values=[""] * len(INPUT_COLUMNS))
        
    def _remove_selected(self):
        """Remove selected rows from input table"""
        for item in self.input_tree.selection():
            self.input_tree.delete(item)
            
    def _edit_input_cell(self, event: tk.Event):
        """Allow editing of input cells on double-click"""
        region = self.input_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.input_tree.identify_row(event.y)
        column_id = self.input_tree.identify_column(event.x)
        if not row_id or not column_id:
            return
        bbox = self.input_tree.bbox(row_id, column_id)
        if not bbox:
            return
        x, y, width, height = bbox
        column_index = int(column_id[1:]) - 1
        current_value = self.input_tree.set(row_id, column_index)
        
        entry = ttk.Entry(self.input_tree)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()
        entry.place(x=x, y=y, width=width, height=height)
        entry.bind("<Return>", lambda e: self._finish_edit_input(entry, row_id, column_index))
        entry.bind("<FocusOut>", lambda e: self._finish_edit_input(entry, row_id, column_index))
        
    def _finish_edit_input(self, entry: ttk.Entry, row_id: str, column_index: int):
        """Finish editing an input cell"""
        new_value = entry.get()
        entry.destroy()
        self.input_tree.set(row_id, column_index, new_value)
        
    def _delete_selected_rows(self, event: tk.Event):
        """Delete selected rows when Delete key is pressed"""
        self._remove_selected()
        
    def _paste_rows(self):
        """Paste rows from clipboard"""
        try:
            raw = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showinfo("Paste Rows", "Clipboard does not contain text data.")
            return
        rows = self._parse_clipboard_rows(raw)
        if not rows:
            messagebox.showinfo("Paste Rows", "No tabular rows detected in the clipboard.")
            return
        for row in rows:
            values = [row.get(col, "") for col, _ in INPUT_COLUMNS]
            self.input_tree.insert("", tk.END, values=values)
            
    def _parse_clipboard_rows(self, raw: str) -> List[Dict[str, Any]]:
        """Parse clipboard data into rows"""
        if not raw:
            return []
            
        reader = csv.reader(io.StringIO(raw), delimiter="\t")
        rows = [list(row) for row in reader]
        if not rows:
            return []
            
        normalized_targets = [_normalize_header(value) for _, value in INPUT_COLUMNS]
        normalized_sources = [_normalize_header(value) for value in rows[0]]
        
        header_lookup: Dict[str, int] = {}
        data_rows = rows
        if rows and normalized_sources:
            has_header = all(target in normalized_sources for target in normalized_targets)
            if has_header:
                header_lookup = {value: idx for idx, value in enumerate(normalized_sources)}
                data_rows = rows[1:]
                
        if not header_lookup:
            header_lookup = {target: idx for idx, target in enumerate(normalized_targets)}
            
        parsed: List[Dict[str, Any]] = []
        for raw_row in data_rows:
            row_map: Dict[str, Any] = {}
            non_empty = False
            for column_index, (target, (dest_key, _)) in enumerate(zip(normalized_targets, INPUT_COLUMNS)):
                idx = header_lookup.get(target, column_index)
                cell_value = raw_row[idx] if idx < len(raw_row) else ""
                if isinstance(cell_value, str):
                    cell_value = cell_value.strip()
                row_map[dest_key] = cell_value
                if cell_value not in ("", None):
                    non_empty = True
            if non_empty:
                parsed.append(row_map)
        return parsed
        
    def _collect_inputs(self) -> List[Dict[str, Any]]:
        """Collect all input rows from the table"""
        rows: List[Dict[str, Any]] = []
        for item in self.input_tree.get_children():
            values = self.input_tree.item(item, "values")
            row = {col: values[idx] for idx, (col, _) in enumerate(INPUT_COLUMNS)}
            if any(value not in ("", None) for value in row.values()):
                rows.append(row)
        return rows
        
    def _run_automation(self):
        """Start the automation in a background thread"""
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Automation", "Worker already running.")
            return
        data_list = self._collect_inputs()
        if not data_list:
            messagebox.showinfo("Automation", "Add at least one input row.")
            return
            
        self._clear_results()
        self.is_running = True
        self._set_controls_enabled(False)
        
        def worker():
            try:
                run_automation_batch(
                    data_list,
                    status_callback=self._update_status,
                    result_callback=self._add_result_row,
                    stop_check=lambda: not self.is_running
                )
                self.root.after(0, lambda: self._handle_completion(len(data_list)))
            except Exception as exc:
                self.root.after(0, lambda: self._handle_error(str(exc)))
                
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
        
    def _update_status(self, message: str):
        """Update status from automation thread"""
        self.root.after(0, lambda: self.status_var.set(message))
        
    def _add_result_row(self, data: Dict[str, Any]):
        """Add a result row to the results table"""
        def update_gui():
            self.result_rows.append(data)
            if not self.result_columns:
                self.result_columns = list(data.keys())
                self.result_tree.configure(columns=self.result_columns)
                for col in self.result_columns:
                    self.result_tree.heading(col, text=col)
                    self.result_tree.column(col, width=160, anchor=tk.CENTER)
            values = [data.get(col, "") for col in self.result_columns]
            self.result_tree.insert("", tk.END, values=values)
        
        self.root.after(0, update_gui)
        
    def _clear_results(self):
        """Clear all results"""
        self.result_rows.clear()
        self.result_columns.clear()
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.result_tree.configure(columns=())
        
    def _stop_automation(self):
        """Stop the running automation"""
        self.is_running = False
        self.status_var.set("Stopping...")
        
    def _handle_completion(self, total_rows: int):
        """Handle successful completion of automation"""
        self.status_var.set(f"Completed {total_rows} rows")
        messagebox.showinfo("Success", f"Automation completed!\nProcessed {total_rows} rows.")
        self._set_controls_enabled(True)
        
    def _copy_results(self):
        """Copy results to clipboard"""
        df = pd.DataFrame(self.result_rows)
        if df.empty:
            messagebox.showinfo("Copy Results", "No results to copy yet.")
            return
        df = df.fillna("")
        df = df.astype(str)
        buffer = io.StringIO()
        df.to_csv(buffer, sep="\t", index=False, lineterminator="\n", header=False)
        self.root.clipboard_clear()
        self.root.clipboard_append(buffer.getvalue())
        messagebox.showinfo("Copy Results", "Results copied to clipboard.")
        
    def _set_controls_enabled(self, enabled: bool):
        """Enable/disable controls during automation"""
        state = tk.NORMAL if enabled else tk.DISABLED
        for widget in (self.btn_run, self.btn_add, self.btn_remove, self.btn_paste, self.btn_copy):
            widget.configure(state=state)
        self.btn_stop.configure(state=tk.DISABLED if enabled else tk.NORMAL)
        
    def _handle_error(self, message: str):
        """Handle errors during automation"""
        self.status_var.set("Error occurred")
        messagebox.showerror("Error", f"An error occurred during automation:\n{message}")
        self._set_controls_enabled(True)
        
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()


def launch_gui():
    """Launch the GUI application"""
    app = BuckelingAutomationGUI()
    app.run()


if __name__ == "__main__":
    launch_gui()
