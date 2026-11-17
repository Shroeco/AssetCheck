import pytest
from assetcheck.config import validate_config


def test_valid_config_returns_none():
    config = {
        "categories": {
            "Textures": {"extensions": [".png", ".jpg"]},
            "Audio": {"extensions": [".wav", ".mp3"]}
        }
    }

    assert validate_config(config) is None


def test_root_must_be_dictionary():
    with pytest.raises(ValueError):
        validate_config(["Textures"])


def test_categories_must_be_dictionary():
    with pytest.raises(ValueError):
        validate_config({"categories": ["Textures"]})


def test_categories_key_is_required():
    with pytest.raises(ValueError):
        validate_config({})


@pytest.mark.parametrize("category", ["", "   ", 123])
def test_category_name_must_be_non_empty_string(category):
    config = {"categories": {category: {"extensions": [".png"]}}}

    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize("category_config", [
    "not a dictionary",
    [],
    None
])
def test_category_configuration_must_be_dictionary(category_config):
    config = {"categories": {"Textures": category_config}}

    with pytest.raises(ValueError):
        validate_config(config)


def test_extensions_key_is_required():
    config = {"categories": {"Textures": {}}}

    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize("extensions", [
    ".png",
    None,
    123,
    {}
])
def test_extensions_must_be_list(extensions):
    config = {"categories": {"Textures": {"extensions": extensions}}}

    with pytest.raises(ValueError):
        validate_config(config)


def test_empty_extensions_list_is_valid():
    config = {"categories": {"Custom": {"extensions": []}}}

    assert validate_config(config) is None


@pytest.mark.parametrize("extension", [
    "",
    "   ",
    123,
    None
])
def test_extension_must_be_non_empty_string(extension):
    config = {"categories": {"Textures": {"extensions": [extension]}}}

    with pytest.raises(ValueError):
        validate_config(config)


def test_extension_must_start_with_period():
    config = {"categories": {"Textures": {"extensions": ["png"]}}}

    with pytest.raises(ValueError):
        validate_config(config)


def test_duplicate_extensions_are_rejected():
    config = {
        "categories": {
            "Textures": {"extensions": [".png", ".jpg", ".png"]}
        }
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_duplicate_extensions_are_case_insensitive():
    config = {
        "categories": {
            "Textures": {"extensions": [".png", ".PNG"]}
        }
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_same_extension_allowed_in_different_categories():
    config = {
        "categories": {
            "Models": {"extensions": [".fbx", ".obj"]},
            "Animations": {"extensions": [".fbx", ".anim"]}
        }
    }

    assert validate_config(config) is None


def test_folder_mappings_must_be_dictionary():
    config = {
        "categories": {},
        "folder_mappings": []
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_folder_mapping_name_must_be_non_empty_string():
    config = {
        "categories": {},
        "folder_mappings": {"": "Textures"}
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_mapped_category_must_be_non_empty_string():
    config = {
        "categories": {},
        "folder_mappings": {"Textures": ""}
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_mapped_category_must_exist():
    config = {
        "categories": {
            "Textures": {"extensions": [".png"]}
        },
        "folder_mappings": {
            "Models": "Audio"
        }
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_valid_folder_mapping_is_accepted():
    config = {
        "categories": {
            "Textures": {"extensions": [".png"]}
        },
        "folder_mappings": {
            "Textures": "Textures"
        }
    }

    assert validate_config(config) is None
