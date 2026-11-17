
from pathlib import Path

from assetcheck.models import ScannedFile, Severity
from assetcheck.validator import validate_files


def test_allowed_extension_produces_no_issue(tmp_path):
    file_path = tmp_path / "character.png"
    scanned_file = ScannedFile(file_path, 1024)

    file_categories = {file_path: "Textures"}
    category_extensions = {"Textures": [".png", ".jpeg"]}

    result = validate_files(
        [scanned_file], file_categories, category_extensions
    )

    assert result == []


def test_unrecognised_extension_produces_info(tmp_path):
    file_path = tmp_path / "character.webp"
    scanned_file = ScannedFile(file_path, 1024)

    file_categories = {file_path: "Textures"}
    category_extensions = {"Textures": [".png", ".jpeg"]}

    result = validate_files(
        [scanned_file], file_categories, category_extensions
    )

    assert len(result) == 1
    assert result[0].severity == Severity.INFO
    assert result[0].check_name == "extension_check"
    assert result[0].actual_value == ".webp"
    assert result[0].expected_value is None


def test_recognised_extension_in_wrong_category_produces_warning(tmp_path):
    file_path = tmp_path / "music.wav"
    scanned_file = ScannedFile(file_path, 2048)

    file_categories = {file_path: "Textures"}
    category_extensions = {
        "Textures": [".png", ".jpeg"],
        "Audio": [".wav", ".ogg"]
    }

    result = validate_files(
        [scanned_file], file_categories, category_extensions
    )

    assert len(result) == 1
    assert result[0].severity == Severity.WARNING
    assert result[0].check_name == "extension_check"
    assert result[0].expected_value == ".png, .jpeg"
    assert result[0].actual_value == ".wav"


def test_missing_category_assignment_is_skipped(tmp_path):
    file_path = tmp_path / "character.png"
    scanned_file = ScannedFile(file_path, 1024)

    category_extensions = {"Textures": [".png", ".jpeg"]}

    result = validate_files(
        [scanned_file], {}, category_extensions
    )

    assert result == []


def test_unconfigured_category_is_skipped(tmp_path):
    file_path = tmp_path / "character.png"
    scanned_file = ScannedFile(file_path, 1024)

    file_categories = {file_path: "CustomCategory"}

    result = validate_files(
        [scanned_file], file_categories, {}
    )

    assert result == []


def test_multiple_files_produce_individual_issues(tmp_path):
    texture_path = tmp_path / "character.png"
    unknown_path = tmp_path / "background.webp"
    misplaced_path = tmp_path / "music.wav"

    scanned_files = [
        ScannedFile(texture_path, 1024),
        ScannedFile(unknown_path, 2048),
        ScannedFile(misplaced_path, 4096)
    ]

    file_categories = {
        texture_path: "Textures",
        unknown_path: "Textures",
        misplaced_path: "Textures"
    }

    category_extensions = {
        "Textures": [".png", ".jpeg"],
        "Audio": [".wav", ".ogg"]
    }

    result = validate_files(
        scanned_files, file_categories, category_extensions
    )

    assert len(result) == 2
    assert result[0].file_path == unknown_path
    assert result[0].severity == Severity.INFO
    assert result[1].file_path == misplaced_path
    assert result[1].severity == Severity.WARNING

def test_uppercase_file_extension_matches_lowercase_configuration(tmp_path):
    file_path = tmp_path / "character.PNG"
    scanned_file = ScannedFile(file_path, 1024)

    file_categories = {file_path: "Textures"}
    category_extensions = {"Textures": [".png", ".jpeg"]}

    result = validate_files([scanned_file], file_categories, category_extensions)

    assert result == []


def test_lowercase_file_extension_matches_uppercase_configuration(tmp_path):
    file_path = tmp_path / "character.png"
    scanned_file = ScannedFile(file_path, 1024)

    file_categories = {file_path: "Textures"}
    category_extensions = {"Textures": [".PNG", ".JPEG"]}

    result = validate_files([scanned_file], file_categories, category_extensions)

    assert result == []


def test_uppercase_configured_extension_is_recognised_in_another_category(tmp_path):
    file_path = tmp_path / "music.wav"
    scanned_file = ScannedFile(file_path, 2048)

    file_categories = {file_path: "Textures"}
    category_extensions = {
        "Textures": [".png", ".jpeg"],
        "Audio": [".WAV", ".OGG"]
    }

    result = validate_files([scanned_file], file_categories, category_extensions)

    assert len(result) == 1
    assert result[0].severity == Severity.WARNING
    assert result[0].actual_value == ".wav"