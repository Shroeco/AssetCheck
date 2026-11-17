
from pathlib import Path

from assetcheck.models import ScannedFile, ScanResult
from assetcheck.scanner import scan_directory

import pytest

def test_scan_directory_finds_files(tmp_path: Path):
    file_one = tmp_path / "character.png"
    file_two = tmp_path / "environment.fbx"

    file_one.write_text("character asset")
    file_two.write_text("environment asset")

    result = scan_directory(tmp_path)

    assert isinstance(result, ScanResult)
    assert len(result.scanned_files) == 2
    assert result.errors == []

    scanned_paths = {file.path for file in result.scanned_files}

    assert scanned_paths == {file_one, file_two}


def test_scan_directory_finds_nested_files(tmp_path: Path):
    nested_directory = tmp_path / "characters"
    nested_directory.mkdir()

    nested_file = nested_directory / "character.png"
    nested_file.write_text("character asset")

    result = scan_directory(tmp_path)

    assert len(result.scanned_files) == 1
    assert result.scanned_files[0].path == nested_file
    assert result.errors == []


def test_scan_directory_handles_empty_directory(tmp_path: Path):
    result = scan_directory(tmp_path)

    assert isinstance(result, ScanResult)
    assert result.scanned_files == []
    assert result.errors == []


def test_scan_directory_skips_directory_symlinks(tmp_path: Path):
    root = tmp_path / "assets"
    root.mkdir()

    nested = root / "characters"
    nested.mkdir()

    root_file = root / "character.png"
    nested_file = nested / "enemy.png"

    root_file.write_text("character")
    nested_file.write_text("enemy")

    symlink = nested / "back_to_root"

    try:
        symlink.symlink_to(root, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlinks are unavailable on this system.")

    result = scan_directory(root)

    assert len(result.scanned_files) == 2
    assert result.errors == []


def test_scan_directory_records_file_inspection_errors(tmp_path: Path, monkeypatch):
    problem_file = tmp_path / "problem.png"
    normal_file = tmp_path / "normal.png"

    problem_file.write_text("problem")
    normal_file.write_text("normal")

    original_stat = Path.stat

    def failing_stat(self, *args, **kwargs):
        if self == problem_file:
            raise PermissionError("Permission denied")

        return original_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", failing_stat)

    result = scan_directory(tmp_path)

    assert len(result.scanned_files) == 1
    assert result.scanned_files[0].path == normal_file

    assert len(result.errors) == 1
    assert result.errors[0].path == problem_file
    assert "Permission denied" in result.errors[0].message


def test_scan_directory_continues_after_nested_directory_error(tmp_path: Path, monkeypatch):
    restricted = tmp_path / "restricted"
    accessible = tmp_path / "accessible"

    restricted.mkdir()
    accessible.mkdir()

    accessible_file = accessible / "weapon.png"
    accessible_file.write_text("weapon")

    original_iterdir = Path.iterdir

    def failing_iterdir(self):
        if self == restricted:
            raise PermissionError("Access denied")

        return original_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", failing_iterdir)

    result = scan_directory(tmp_path)

    assert len(result.scanned_files) == 1
    assert result.scanned_files[0].path == accessible_file

    assert len(result.errors) == 1
    assert result.errors[0].path == restricted
    assert "Access denied" in result.errors[0].message


def test_scan_directory_records_entry_inspection_errors_two(tmp_path: Path, monkeypatch):
    problem_file = tmp_path / "problem.png"
    normal_file = tmp_path / "normal.png"

    problem_file.write_text("problem")
    normal_file.write_text("normal")

    original_is_symlink = Path.is_symlink

    def failing_is_symlink(self):
        if self == problem_file:
            raise PermissionError("Unable to inspect entry")

        return original_is_symlink(self)

    monkeypatch.setattr(Path, "is_symlink", failing_is_symlink)

    result = scan_directory(tmp_path)

    assert len(result.scanned_files) == 1
    assert result.scanned_files[0].path == normal_file

    assert len(result.errors) == 1
    assert result.errors[0].path == problem_file
    assert "Unable to inspect entry" in result.errors[0].message


def test_scan_directory_records_file_inspection_errors_one(tmp_path, monkeypatch):
    good_file = tmp_path / "good.txt"
    error_file = tmp_path / "error.txt"

    good_file.write_text("Valid file")
    error_file.write_text("File that will cause an error")

    original_stat = Path.stat

    def mock_stat(self, *args, **kwargs):
        if self == error_file:
            raise OSError("Permission denied")

        return original_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", mock_stat)

    result = scan_directory(tmp_path)

    assert any(file.path == good_file for file in result.scanned_files)
    assert not any(file.path == error_file for file in result.scanned_files)

    assert len(result.errors) == 1
    assert result.errors[0].path == error_file
    assert result.errors[0].message == "Permission denied"
