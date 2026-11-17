import pytest

from pathlib import Path
from assetcheck.models import ScannedFile, ValidationIssue, Severity, ScanError, ScanResult

def test_scanned_file_valid():
    test_file = ScannedFile(Path("tester.png"), 100)
    assert test_file.name == "tester.png"
    assert test_file.size_bytes == 100

def test_scanned_file_filename():
    test_file = ScannedFile(Path("tester.png"), 100)
    assert test_file.name == "tester.png"

def test_scanned_file_extension():
    test_file = ScannedFile(Path("tester.png"), 100)
    assert test_file.extension == ".png"

def test_scanned_file_valid_zero_bytes():
    test_file = ScannedFile(Path("tester.png"), 0)
    assert test_file.name == "tester.png"
    assert test_file.size_bytes == 0

def test_scanned_file_negative_size():
    with pytest.raises(ValueError):
        ScannedFile(Path("tester.png"), -1)

def test_validation_constructs():
    test_validation = ValidationIssue(Path("tester file.png"), "Naming Convention", Severity.ERROR, "Invalid space in filename.")
    assert test_validation.file_path == Path("tester file.png")
    assert test_validation.check_name == "Naming Convention"
    assert test_validation.severity == Severity.ERROR
    assert test_validation.message == "Invalid space in filename."

def test_validation_nones():
    test_validation = ValidationIssue(Path("tester file.png"), "Naming Convention", Severity.ERROR, "Invalid space in filename.")
    assert test_validation.actual_value is None
    assert test_validation.expected_value is None

def test_validation_severity():
    assert Severity.WARNING.value == "warning"
    assert Severity.ERROR.value == "error"
    assert Severity.INFO.value == "info"

def test_scan_error_valid():
    error = ScanError(Path("tester.png"), "File inaccessible with current permissions.")
    assert error.path == Path("tester.png")
    assert error.message == "File inaccessible with current permissions."

def test_scan_result_with_files_and_errors():
    test_file_one = ScannedFile(Path("tester1.png"), 100)
    test_file_two = ScannedFile(Path("tester2.png"), 100)
    test_file_three = ScannedFile(Path("tester3.png"), 100)
    test_file_four = ScannedFile(Path("tester4.png"), 100)
    test_file_five = ScannedFile(Path("tester5.png"), 100)
    error_one = ScanError(Path("tester6.png"), "File inaccessible with current permissions.")
    error_two = ScanError(Path("tester7.png"), "File inaccessible with current permissions.")
    result = ScanResult([test_file_one, test_file_two, test_file_three, test_file_four, test_file_five], [error_one, error_two])
    assert result.scanned_files[1] == test_file_two
    assert result.scanned_files[4] == test_file_five
    assert len(result.scanned_files) == 5
    assert result.errors[0] == error_one
    assert result.errors[1] == error_two
    assert len(result.errors) == 2

def test_scan_result_empty():
    result = ScanResult([],[])
    assert not result.scanned_files
    assert not result.errors