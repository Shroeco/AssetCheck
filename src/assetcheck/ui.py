
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from tkinter import ttk
from pathlib import Path

from assetcheck.scanner import scan_directory
from assetcheck.models import ScanResult, ScannedFile, ScanError
from assetcheck.config import load_config, validate_config
from assetcheck.categoriser import categorise_files
from assetcheck.validator import validate_files


class AssetCheckApp:

    
    def configure_theme(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        self.root.configure(bg="#17191F")

        style.configure(
            ".",
            background="#17191F",
            foreground="#E6E8ED",
            font=("Segoe UI", 10)
        )

        # Main background
        style.configure(
            "TFrame",
            background="#17191F"
        )

        # Reusable panels
        style.configure(
            "Panel.TFrame",
            background="#222630",
            relief="solid",
            borderwidth=1,
            bordercolor="#303541",
            lightcolor="#303541",
            darkcolor="#303541"
        )

        # Standard labels
        style.configure(
            "TLabel",
            background="#17191F",
            foreground="#E6E8ED"
        )

        style.configure(
            "PanelHeading.TLabel",
            background="#222630",
            foreground="#FFFFFF",
            font=("Segoe UI", 11, "bold")
        )

        # Directory display
        style.configure(
            "Directory.TLabel",
            background="#222630",
            foreground="#E6E8ED",
            padding=10,
            relief="solid",
            borderwidth=1,
            bordercolor="#303541",
            lightcolor="#303541",
            darkcolor="#303541"
        )

        # Buttons
        style.configure(
            "TButton",
            background="#3978E8",
            foreground="#FFFFFF",
            padding=(14, 8),
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            focuscolor="#508BFA"
        )

        style.map(
            "TButton",
            background=[
                ("active", "#508BFA"),
                ("disabled", "#303541")
            ],
            foreground=[
                ("disabled", "#929BAA")
            ]
        )

        # Results table
        style.configure(
            "Treeview",
            background="#222630",
            foreground="#E6E8ED",
            fieldbackground="#222630",
            borderwidth=0,
            rowheight=32,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#303541",
            foreground="#FFFFFF",
            relief="flat",
            padding=9,
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#3978E8")],
            foreground=[("selected", "#FFFFFF")]
        )

        # Scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background="#303541",
            troughcolor="#17191F",
            bordercolor="#17191F",
            lightcolor="#303541",
            darkcolor="#303541",
            arrowcolor="#AAB2C0",
            gripcount=0,
            arrowsize=12
        )

        style.map(
            "Vertical.TScrollbar",
            background=[
                ("active", "#414957"),
                ("pressed", "#3978E8")
            ],
            arrowcolor=[
                ("active", "#FFFFFF")
            ]
        )

        # Summary cards
        style.configure(
            "SummaryTitle.TLabel",
            background="#222630",
            foreground="#AAB2C0",
            font=("Segoe UI", 9)
        )

        summary_colours = {
            "Total": "#E6E8ED",
            "Passed": "#4ADE80",
            "Warnings": "#FBBF24",
            "Errors": "#F87171"
        }

        for name, colour in summary_colours.items():
            style.configure(
                f"Summary{name}.TLabel",
                background="#222630",
                foreground=colour,
                font=("Segoe UI", 17, "bold")
            )


    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AssetCheck")
        self.root.geometry("1000x650")
        self.root.minsize(500, 325)

        self.configure_theme()

        self.config = None

        config_path = Path(__file__).resolve().parent / "default_config.json"

        try:
            self.config = load_config(config_path)
            validate_config(self.config)

        except (OSError, ValueError) as error:
            mb.showerror(
                title="Configuration Error",
                message=f"Unable to load or validate configuration:\n{error}"
            )

        if self.config is not None:
            self.category_extensions = {
                category: details["extensions"]
                for category, details in self.config["categories"].items()
            }
            self.folder_mappings = self.config.get("folder_mappings", {})
        else:
            self.category_extensions = {}
            self.folder_mappings = {}

        self.directory_path = ""
        self.scan_path: Path | None = None

        # Directory selection panel
        self.directory_frame = ttk.Frame(self.root, padding=10)
        self.directory_frame.pack(fill=tk.X, padx=20, pady=15)

        self.directory_frame.grid_columnconfigure(0, weight=1)

        # Selected directory display
        self.label = ttk.Label(
            self.directory_frame,
            text="No directory selected.",
            anchor=tk.W,
            style="Directory.TLabel"
        )
        self.label.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky=tk.NSEW,
            padx=(10, 15)
        )

        # Browse button
        self.browse_button = ttk.Button(
            self.directory_frame,
            text="Browse",
            command=self.browse_directory
        )
        self.browse_button.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            pady=(0, 5)
        )

        # Scan button
        self.scan_button = ttk.Button(
            self.directory_frame,
            text="Scan",
            command=self.scan_selected_directory
        )

        if self.config is None:
            self.scan_button.config(state=tk.DISABLED)

        self.scan_button.grid(
            row=1,
            column=1,
            sticky=tk.EW,
            pady=(5, 0)
        )

        # Scan summary section
        self.summary_frame = ttk.Frame(self.root, padding=5)
        self.summary_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        summary_cards = [
            ("total", "Total Files", "Total"),
            ("passed", "Passed", "Passed"),
            ("warnings", "Warnings", "Warnings"),
            ("errors", "Errors", "Errors")
        ]

        self.summary_values = {}

        for column, (key, title, style_name) in enumerate(summary_cards):
            self.summary_frame.grid_columnconfigure(column, weight=1)

            card = ttk.Frame(
                self.summary_frame,
                style="Panel.TFrame",
                padding=12
            )
            card.grid(
                row=0,
                column=column,
                sticky=tk.NSEW,
                padx=5
            )

            title_label = ttk.Label(
                card,
                text=title,
                style="SummaryTitle.TLabel"
            )
            title_label.pack(anchor=tk.W)

            value_label = ttk.Label(
                card,
                text="0",
                style=f"Summary{style_name}.TLabel"
            )
            value_label.pack(anchor=tk.W, pady=(4, 0))

            self.summary_values[key] = value_label

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.frame.grid_columnconfigure(0, weight=3)
        self.frame.grid_columnconfigure(1, weight=2)
        self.frame.grid_rowconfigure(0, weight=1)

        # Left panel: results table
        self.left_frame = ttk.Frame(self.frame, style="Panel.TFrame", padding=12)
        self.left_frame.grid(column=0, row=0, sticky=tk.NSEW)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)

        self.table = ttk.Treeview(
            self.left_frame,
            columns=("File", "Type", "Size", "Status"),
            height=15,
            show="headings"
        )
        self.table.grid(column=0, row=0, sticky=tk.NSEW)

        self.table.heading("File", text="File")
        self.table.heading("Type", text="Type")
        self.table.heading("Size", text="Size")
        self.table.heading("Status", text="Status")

        self.table.bind("<<TreeviewSelect>>", self.on_item_selected)

        v_scrollbar = ttk.Scrollbar(
            self.left_frame,
            orient=tk.VERTICAL,
            command=self.table.yview
        )
        v_scrollbar.grid(column=1, row=0, sticky=tk.NS)

        self.table.config(yscrollcommand=v_scrollbar.set)

        # Right panel: selected item details
        self.right_frame = ttk.Frame(self.frame, style="Panel.TFrame", padding=12)
        self.right_frame.grid(column=1, row=0, sticky=tk.NSEW)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        self.heading_label = ttk.Label(
            self.right_frame,
            text="Selected Item Details",
            style="PanelHeading.TLabel"
        )
        self.heading_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        # Column sizing and alignment
        self.table.column(
            "File", width=240, minwidth=140,
            anchor=tk.W, stretch=True
        )

        self.table.column(
            "Type", width=75, minwidth=60,
            anchor=tk.CENTER, stretch=False
        )

        self.table.column(
            "Size", width=85, minwidth=70,
            anchor=tk.E, stretch=False
        )

        self.table.column(
            "Status", width=105, minwidth=90,
            anchor=tk.CENTER, stretch=False
        )

        # Status row colours
        self.table.tag_configure(
            "Passed",
            background="#1D2D26",
            foreground="#DDF7E7"
        )

        self.table.tag_configure(
            "Warning",
            background="#3B3220",
            foreground="#FFF0C2"
        )

        self.table.tag_configure(
            "Info",
            background="#202F42",
            foreground="#D6E9FF"
        )

        self.table.tag_configure(
            "Error",
            background="#3B2428",
            foreground="#FFDDE0"
        )

        self.table.tag_configure(
            "Scan Error",
            background="#3B2428",
            foreground="#FFDDE0"
        )

        self.details_text = tk.Text(
            self.right_frame,
            wrap=tk.WORD,
            height=20,
            width=35,
            state=tk.DISABLED,
            bg="#222630",
            fg="#E6E8ED",
            insertbackground="#E6E8ED",
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.details_text.grid(row=1, column=0, sticky=tk.NSEW)

        details_scrollbar = ttk.Scrollbar(
            self.right_frame,
            orient=tk.VERTICAL,
            command=self.details_text.yview
        )
        details_scrollbar.grid(row=1, column=1, sticky=tk.NS)

        self.details_text.config(yscrollcommand=details_scrollbar.set)

        self.result_items = {}

    def update_details(self, text: str) -> None:
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert("1.0", text)
        self.details_text.config(state=tk.DISABLED)

    def browse_directory(self):
        directory_path = fd.askdirectory()

        if directory_path:
            self.directory_path = directory_path
            self.scan_path = Path(self.directory_path)
            self.label.config(text=self.directory_path)

    def scan_selected_directory(self) -> None:
        if not self.directory_path:
            mb.showwarning(
                title=None,
                message="No directory selected. Scan cannot proceed."
            )
            return

        if self.config is None:
            mb.showerror(
                title="Configuration Error",
                message="Cannot scan without a valid configuration."
            )
            return

        try:
            self.scan_result = scan_directory(self.scan_path)

            self.file_categories = categorise_files(
                self.scan_result.scanned_files,
                self.folder_mappings,
                self.scan_path
            )

            self.validation_issues = validate_files(
                self.scan_result.scanned_files,
                self.file_categories,
                self.category_extensions
            )

        except Exception as error:
            # Remove old results so they aren't mistaken for this scan.
            self.table.delete(*self.table.get_children())
            self.result_items.clear()

            self.file_categories = {}
            self.validation_issues = []

            for summary_value in self.summary_values.values():
                summary_value.config(text="0")

            self.update_details("The scan could not be completed.")

            mb.showerror(
                title="Scan Error",
                message=f"An unexpected error occurred during scanning:\n{error}"
            )
            return

        self.display_scan_results(self.scan_result)

    def format_file_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"

        size = size_bytes / 1024
        units = ["KB", "MB", "GB", "TB"]

        for unit in units:
            if size < 1024 or unit == "TB":
                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} TB"

    def display_scan_results(self, result: ScanResult) -> None:
        self.table.delete(*self.table.get_children())
        self.result_items.clear()

        issues_by_path = {}

        summary_counts = {"total": len(result.scanned_files), "passed": 0, "warnings": 0, "errors": 0}

        for issue in self.validation_issues:
            if issue.file_path not in issues_by_path:
                issues_by_path[issue.file_path] = []

            issues_by_path[issue.file_path].append(issue)

        for file in result.scanned_files:
            file_issues = issues_by_path.get(file.path, [])

            if any(issue.severity.value == "error" for issue in file_issues):
                status = "Error"
            elif any(issue.severity.value == "warning" for issue in file_issues):
                status = "Warning"
            elif any(issue.severity.value == "info" for issue in file_issues):
                status = "Info"
            else:
                status = "Passed"

            if status in ("Passed", "Info"):
                summary_counts["passed"] += 1
            elif status == "Warning":
                summary_counts["warnings"] += 1
            elif status == "Error":
                summary_counts["errors"] += 1

            row_data = (file.name, file.extension, self.format_file_size(file.size_bytes), status)
            item_id = self.table.insert("", "end", values=row_data,  tags=(status,))
            self.result_items[item_id] = file

        for error in result.errors:
            summary_counts["errors"] += 1
            row_data = (error.path.name, "-", "-", "Scan Error")
            item_id = self.table.insert("", "end", values=row_data, tags=("Scan Error",))
            self.result_items[item_id] = error

        # Update summary cards
        for key, count in summary_counts.items():
            self.summary_values[key].config(text=str(count))

        self.update_details("Select a file to view its details.")

    def on_item_selected(self, event) -> None:
        selected_items = self.table.selection()

        if not selected_items:
            self.update_details("No item selected.")
            return

        result_object = self.result_items[selected_items[0]]

        if isinstance(result_object, ScannedFile):
            category = self.file_categories.get(
                result_object.path,
                "Uncategorised"
            )

            file_issues = [
                issue for issue in self.validation_issues
                if issue.file_path == result_object.path
            ]

            if any(issue.severity.value == "error" for issue in file_issues):
                status = "Error"
            elif any(issue.severity.value == "warning" for issue in file_issues):
                status = "Warning"
            elif any(issue.severity.value == "info" for issue in file_issues):
                status = "Info"
            else:
                status = "Passed"

            details = (
                f"Name:\n{result_object.name}\n\n"
                f"Path:\n{result_object.path}\n\n"
                f"Status:\n{status}\n\n"
                f"Category:\n{category}\n\n"
                f"Extension:\n{result_object.extension}\n\n"
                f"Size:\n{result_object.size_bytes} bytes\n\n"
            )

            if file_issues:
                details += "Validation Issues:\n\n"

                for issue in file_issues:
                    details += (
                        f"{issue.severity.value.upper()}: {issue.message}\n"
                        f"Expected: {issue.expected_value}\n"
                        f"Actual: {issue.actual_value}\n\n"
                    )
            else:
                details += "Validation:\nNo validation issues."

            self.update_details(details)

        elif isinstance(result_object, ScanError):
            details = (
                f"Name:\n{result_object.path.name}\n\n"
                f"Path:\n{result_object.path}\n\n"
                f"Status:\nScan Error\n\n"
                f"Message:\n{result_object.message}"
            )

            self.update_details(details)
