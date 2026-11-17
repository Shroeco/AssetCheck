import json
import pytest
from pathlib import Path
from assetcheck.config import load_config


def test_load_config_returns_categories(tmp_path):
    config_path = tmp_path / "config.json"

    config_data = {
        "categories": {
            "Textures": {
                "extensions": [".png", ".jpg"]
            },
            "Audio": {
                "extensions": [".wav", ".mp3"]
            }
        }
    }

    config_path.write_text(json.dumps(config_data))

    result = load_config(config_path)

    assert result == config_data


def test_load_config_missing_file_raises_error(tmp_path):
    config_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_config(config_path)


def test_load_config_invalid_json_raises_error(tmp_path):
    config_path = tmp_path / "invalid.json"
    config_path.write_text("{ invalid json }")

    with pytest.raises(json.JSONDecodeError):
        load_config(config_path)


def test_load_config_empty_json_object(tmp_path):
    config_path = tmp_path / "empty.json"
    config_path.write_text("{}")

    result = load_config(config_path)

    assert result == {}