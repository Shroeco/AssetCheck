from pathlib import Path

from assetcheck.scanner import scan_directory
from assetcheck.categoriser import categorise_files
from assetcheck.validator import validate_files
from assetcheck.models import Severity


def test_full_pipeline_categorises_and_validates_files(tmp_path):
    assets = tmp_path / "Assets"

    textures = assets / "Textures"
    models = assets / "Models"
    animations = models / "Animations"
    misc = assets / "Misc"

    textures.mkdir(parents=True)
    animations.mkdir(parents=True)
    misc.mkdir(parents=True)

    valid_texture = textures / "character.png"
    misplaced_model = textures / "model.obj"
    valid_model = models / "vehicle.fbx"
    unknown_extension = models / "unusual.xyz"
    nested_animation = animations / "walking.fbx"
    uncategorised_file = misc / "readme.txt"

    for file_path in [
        valid_texture,
        misplaced_model,
        valid_model,
        unknown_extension,
        nested_animation,
        uncategorised_file
    ]:
        file_path.write_text("Test asset")

    folder_mappings = {
        "Textures": "Textures",
        "Models": "Models",
        "Models/Animations": "Animations"
    }

    category_extensions = {
        "Textures": [".png", ".jpg"],
        "Models": [".fbx", ".obj"],
        "Animations": [".anim"]
    }

    scan_result = scan_directory(assets)

    file_categories = categorise_files(
        scan_result.scanned_files,
        folder_mappings,
        assets
    )

    validation_issues = validate_files(
        scan_result.scanned_files,
        file_categories,
        category_extensions
    )

    assert len(scan_result.scanned_files) == 6
    assert len(scan_result.errors) == 0

    assert file_categories == {
        valid_texture: "Textures",
        misplaced_model: "Textures",
        valid_model: "Models",
        unknown_extension: "Models",
        nested_animation: "Animations"
    }

    assert len(validation_issues) == 3

    issues_by_file = {
        issue.file_path: issue
        for issue in validation_issues
    }

    assert issues_by_file[misplaced_model].severity == Severity.WARNING
    assert issues_by_file[unknown_extension].severity == Severity.INFO
    assert issues_by_file[nested_animation].severity == Severity.WARNING

    assert uncategorised_file not in file_categories


def test_full_pipeline_handles_empty_directory(tmp_path):
    scan_result = scan_directory(tmp_path)

    file_categories = categorise_files(
        scan_result.scanned_files,
        {"Models": "Models"},
        tmp_path
    )

    validation_issues = validate_files(
        scan_result.scanned_files,
        file_categories,
        {"Models": [".fbx"]}
    )

    assert scan_result.scanned_files == []
    assert scan_result.errors == []
    assert file_categories == {}
    assert validation_issues == []


def test_full_pipeline_handles_directory_with_only_uncategorised_files(tmp_path):
    misc = tmp_path / "Misc"
    misc.mkdir()

    file_path = misc / "readme.txt"
    file_path.write_text("This file has no category mapping.")

    scan_result = scan_directory(tmp_path)

    file_categories = categorise_files(
        scan_result.scanned_files,
        {"Models": "Models"},
        tmp_path
    )

    validation_issues = validate_files(
        scan_result.scanned_files,
        file_categories,
        {"Models": [".fbx"]}
    )

    assert len(scan_result.scanned_files) == 1
    assert file_categories == {}
    assert validation_issues == []