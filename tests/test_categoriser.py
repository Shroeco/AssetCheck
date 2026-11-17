from pathlib import Path

from assetcheck.categoriser import categorise_files
from assetcheck.models import ScannedFile


def test_file_inside_mapped_folder_is_categorised():
    file = ScannedFile(Path("Assets/Models/character.fbx"), 1024)

    result = categorise_files(
        [file],
        {"Models": "Models"},
        Path("Assets")
    )

    assert result == {
        Path("Assets/Models/character.fbx"): "Models"
    }


def test_file_inside_nested_mapped_folder_is_categorised():
    file = ScannedFile(
        Path("Assets/Models/Animations/walking.fbx"),
        2048
    )

    result = categorise_files(
        [file],
        {"Models/Animations": "Animations"},
        Path("Assets")
    )

    assert result == {
        Path("Assets/Models/Animations/walking.fbx"): "Animations"
    }


def test_deepest_matching_folder_takes_priority():
    file = ScannedFile(
        Path("Assets/Models/Animations/walking.fbx"),
        2048
    )

    result = categorise_files(
        [file],
        {
            "Models": "Models",
            "Models/Animations": "Animations"
        },
        Path("Assets")
    )

    assert result == {
        Path("Assets/Models/Animations/walking.fbx"): "Animations"
    }


def test_file_outside_mapped_folders_is_excluded():
    file = ScannedFile(Path("Assets/Misc/readme.txt"), 512)

    result = categorise_files(
        [file],
        {"Models": "Models"},
        Path("Assets")
    )

    assert result == {}


def test_empty_folder_mappings_returns_empty_dictionary():
    file = ScannedFile(Path("Assets/Models/character.fbx"), 1024)

    result = categorise_files(
        [file],
        {},
        Path("Assets")
    )

    assert result == {}


def test_multiple_files_are_categorised_correctly():
    files = [
        ScannedFile(Path("Assets/Models/character.fbx"), 1024),
        ScannedFile(Path("Assets/Textures/character.png"), 2048),
        ScannedFile(Path("Assets/Misc/readme.txt"), 512)
    ]

    result = categorise_files(
        files,
        {
            "Models": "Models",
            "Textures": "Textures"
        },
        Path("Assets")
    )

    assert result == {
        Path("Assets/Models/character.fbx"): "Models",
        Path("Assets/Textures/character.png"): "Textures"
    }


def test_folder_name_does_not_match_partial_folder_name():
    file = ScannedFile(
        Path("Assets/OldModels/character.fbx"),
        1024
    )

    result = categorise_files(
        [file],
        {"Models": "Models"},
        Path("Assets")
    )

    assert result == {}


def test_folder_above_scan_root_does_not_match():
    file = ScannedFile(
        Path("Assets/Models/Textures/character.png"),
        1024
    )

    result = categorise_files(
        [file],
        {"Models": "Models"},
        Path("Assets/Models")
    )

    assert result == {}