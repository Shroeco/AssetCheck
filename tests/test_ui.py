from pathlib import Path
from types import SimpleNamespace

import pytest
from assetcheck.models import ScanResult, ScanError
from assetcheck.ui import AssetCheckApp

class FakeTable:
    """A lightweight replacement for the Treeview used in UI tests."""

    def __init__(self):
        self.items = {}
        self.next_id = 0
        self.selected_items = ()

    def delete(self, *item_ids):
        for item_id in item_ids:
            self.items.pop(item_id, None)

    def get_children(self):
        return tuple(self.items.keys())

    def insert(self, parent, index, values, tags=()):
        self.next_id += 1
        item_id = f"item_{self.next_id}"
        self.items[item_id] = values
        return item_id

    def item(self, item_id, option=None):
        if option == "values":
            return self.items[item_id]

        return {"values": self.items[item_id]}

    def selection(self):
        return self.selected_items

    def select(self, item_id):
        self.selected_items = (item_id,)


@pytest.fixture
def app():
    """Create an AssetCheckApp-like object without opening a window."""

    application = SimpleNamespace(
        directory_path="",
        scan_path=None,
        config={"categories": {}},
        category_extensions={
            "Textures": [".png", ".jpg"],
            "Models": [".fbx", ".obj"],
            "Animations": [".anim"]
        },
        folder_mappings={
            "Textures": "Textures",
            "Models": "Models",
            "Models/Animations": "Animations"
        },
        table=FakeTable(),
        result_items={},
        validation_issues=[],
        file_categories={},
        details=""
    )

    application.update_details = lambda text: setattr(
        application, "details", text
    )

    application.display_scan_results = lambda result: (AssetCheckApp.display_scan_results(application, result))

    application.format_file_size = lambda size_bytes: (AssetCheckApp.format_file_size(application, size_bytes))

    application.summary_values = {}

    for key in ("total", "passed", "warnings", "errors"):
        label = SimpleNamespace(value="0")
        label.config = lambda label=label, **kwargs: setattr(
            label, "value", kwargs["text"]
        )
        application.summary_values[key] = label
    
    return application


def test_repeated_scan_does_not_duplicate_results(app, tmp_path):
    assets = tmp_path / "Assets"
    models = assets / "Models"
    models.mkdir(parents=True)

    (models / "character.fbx").write_text("Model")
    (models / "vehicle.obj").write_text("Vehicle")

    app.directory_path = str(assets)
    app.scan_path = assets

    AssetCheckApp.scan_selected_directory(app)

    first_scan_count = len(app.table.get_children())

    AssetCheckApp.scan_selected_directory(app)

    second_scan_count = len(app.table.get_children())

    assert first_scan_count == 2
    assert second_scan_count == 2
    assert len(app.result_items) == 2


def test_scanning_different_directory_replaces_previous_results(app, tmp_path):
    first_directory = tmp_path / "First"
    second_directory = tmp_path / "Second"

    (first_directory / "Models").mkdir(parents=True)
    (second_directory / "Models").mkdir(parents=True)

    first_file = first_directory / "Models" / "character.fbx"
    second_file = second_directory / "Models" / "vehicle.obj"

    first_file.write_text("Character")
    second_file.write_text("Vehicle")

    app.directory_path = str(first_directory)
    app.scan_path = first_directory

    AssetCheckApp.scan_selected_directory(app)

    first_results = [
        app.table.item(item, "values")[0]
        for item in app.table.get_children()
    ]

    assert first_file.name in first_results

    app.directory_path = str(second_directory)
    app.scan_path = second_directory

    AssetCheckApp.scan_selected_directory(app)

    second_results = [
        app.table.item(item, "values")[0]
        for item in app.table.get_children()
    ]

    assert len(second_results) == 1
    assert second_file.name in second_results
    assert first_file.name not in second_results
    assert len(app.result_items) == 1


def test_browsing_cancelled_does_not_change_selected_directory(monkeypatch):
    original_directory = Path("original_directory")

    application = SimpleNamespace(
        directory_path=str(original_directory),
        scan_path=original_directory,
        label=SimpleNamespace(config=lambda **kwargs: None)
    )

    monkeypatch.setattr(
        "assetcheck.ui.fd.askdirectory",
        lambda: ""
    )

    AssetCheckApp.browse_directory(application)

    assert application.scan_path == original_directory
    assert application.directory_path == str(original_directory)

def test_scanning_empty_directory_displays_no_results(app, tmp_path):
    empty_directory = tmp_path / "Empty"
    empty_directory.mkdir()

    app.directory_path = str(empty_directory)
    app.scan_path = empty_directory

    AssetCheckApp.scan_selected_directory(app)

    assert len(app.table.get_children()) == 0
    assert len(app.result_items) == 0
    assert app.details == "Select a file to view its details."

def test_scan_errors_are_displayed_in_results(app, tmp_path, monkeypatch):
    error_path = tmp_path / "inaccessible_folder"
    scan_error = ScanError(
        path=error_path,
        message="Permission denied."
    )

    fake_result = ScanResult(
        scanned_files=[],
        errors=[scan_error]
    )

    monkeypatch.setattr(
        "assetcheck.ui.scan_directory",
        lambda path: fake_result
    )

    app.directory_path = str(tmp_path)
    app.scan_path = tmp_path

    AssetCheckApp.scan_selected_directory(app)

    displayed_items = app.table.get_children()

    assert len(displayed_items) == 1

    row_values = app.table.item(displayed_items[0], "values")

    assert row_values[0] == error_path.name
    assert row_values[3] == "Scan Error"
    assert app.result_items[displayed_items[0]] == scan_error

def test_selecting_scan_error_displays_error_details(app, tmp_path, monkeypatch):
    error_path = tmp_path / "inaccessible_folder"
    scan_error = ScanError(
        path=error_path,
        message="Permission denied."
    )

    fake_result = ScanResult(
        scanned_files=[],
        errors=[scan_error]
    )

    monkeypatch.setattr(
        "assetcheck.ui.scan_directory",
        lambda path: fake_result
    )

    app.directory_path = str(tmp_path)
    app.scan_path = tmp_path

    AssetCheckApp.scan_selected_directory(app)

    item_id = app.table.get_children()[0]
    app.table.select(item_id)

    AssetCheckApp.on_item_selected(app, None)

    assert f"Name:\n{error_path.name}" in app.details
    assert f"Path:\n{error_path}" in app.details
    assert "Status:\nScan Error" in app.details
    assert "Message:\nPermission denied." in app.details

def test_uncategorised_file_is_displayed_as_uncategorised(app, tmp_path):
    assets = tmp_path / "Assets"
    misc = assets / "Misc"
    misc.mkdir(parents=True)

    file_path = misc / "notes.txt"
    file_path.write_text("Some notes")

    app.directory_path = str(assets)
    app.scan_path = assets

    AssetCheckApp.scan_selected_directory(app)

    item_id = app.table.get_children()[0]
    row_values = app.table.item(item_id, "values")

    assert row_values[0] == file_path.name
    assert row_values[3] == "Passed"

    app.table.select(item_id)
    AssetCheckApp.on_item_selected(app, None)

    assert "Status:\nPassed" in app.details
    assert "Category:\nUncategorised" in app.details
    assert "No validation issues." in app.details


def test_validation_warning_is_displayed_in_results(app, tmp_path):
    assets = tmp_path / "Assets"
    textures = assets / "Textures"
    textures.mkdir(parents=True)

    file_path = textures / "incorrect_model.fbx"
    file_path.write_text("Model")

    app.directory_path = str(assets)
    app.scan_path = assets

    AssetCheckApp.scan_selected_directory(app)

    item_id = app.table.get_children()[0]
    row_values = app.table.item(item_id, "values")

    assert row_values[0] == file_path.name
    assert row_values[3] == "Warning"

    app.table.select(item_id)
    AssetCheckApp.on_item_selected(app, None)

    assert "Status:\nWarning" in app.details
    assert "WARNING:" in app.details
    assert "File extension is not permitted for this category." in app.details


def test_unknown_extension_is_displayed_as_info(app, tmp_path):
    assets = tmp_path / "Assets"
    models = assets / "Models"
    models.mkdir(parents=True)

    file_path = models / "unknown.custom"
    file_path.write_text("Unknown format")

    app.directory_path = str(assets)
    app.scan_path = assets

    AssetCheckApp.scan_selected_directory(app)

    item_id = app.table.get_children()[0]
    row_values = app.table.item(item_id, "values")

    assert row_values[0] == file_path.name
    assert row_values[3] == "Info"

    app.table.select(item_id)
    AssetCheckApp.on_item_selected(app, None)

    assert "Status:\nInfo" in app.details
    assert "INFO:" in app.details
    assert "File extension is not configured for categorisation." in app.details

def test_unexpected_scan_error_is_handled_without_crashing(
    app, tmp_path, monkeypatch
):
    app.directory_path = str(tmp_path)
    app.scan_path = tmp_path

    for summary_value in app.summary_values.values():
        summary_value.value = "5"

    monkeypatch.setattr(
        "assetcheck.ui.scan_directory",
        lambda path: (_ for _ in ()).throw(RuntimeError("Unexpected failure"))
    )

    error_messages = []

    monkeypatch.setattr(
        "assetcheck.ui.mb.showerror",
        lambda **kwargs: error_messages.append(kwargs["message"])
    )

    AssetCheckApp.scan_selected_directory(app)

    assert len(app.table.get_children()) == 0
    assert len(app.result_items) == 0
    assert app.details == "The scan could not be completed."
    assert len(error_messages) == 1
    assert "Unexpected failure" in error_messages[0]
    assert all(
        summary_value.value == "0"
        for summary_value in app.summary_values.values())

@pytest.mark.parametrize(
    ("size_bytes", "expected"),
    [
        (0, "0 B"),
        (500, "500 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1048576, "1.0 MB"),
        (1073741824, "1.0 GB"),
    ]
)
def test_format_file_size(app, size_bytes, expected):
    assert AssetCheckApp.format_file_size(app, size_bytes) == expected