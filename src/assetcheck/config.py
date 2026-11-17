import json
from pathlib import Path

def load_config(config_path: Path) -> dict:
    with config_path.open() as file:
        categories = json.load(file)

    return categories

def validate_config(config: dict) -> None:
    if not isinstance(config, dict):
        raise ValueError("The config loaded is not a dictionary.")
    elif not isinstance(config.get("categories"), dict):
        raise ValueError("Within the loaded config there is no categories dictionary.")
    elif "folder_mappings" in config and not isinstance(config["folder_mappings"], dict):
        raise ValueError("Folder mappings must be a dictionary.")

    for category in config["categories"]:
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category name is not a non-empty string.")

        category_config = config["categories"][category]

        if not isinstance(category_config, dict):
            raise ValueError("The category isn't a dictionary.")
        else:
            if "extensions" not in category_config:
                raise ValueError("There is no extensions key in this category.")
            elif not isinstance(category_config.get("extensions"), list):
                raise ValueError("There is no list of extensions in this category.")

            seen_extensions = set()

            for extension in category_config.get("extensions"):
                if not isinstance(extension, str) or not extension.strip():
                    raise ValueError("Extension is not a non-empty string.")
                elif not extension.startswith("."):
                    raise ValueError("Extension doesn't start with '.'.")

                ext = extension.lower()

                if ext in seen_extensions:
                    raise ValueError("This extension is already within the category, no duplicates allowed.")
                else:
                    seen_extensions.add(ext)

    for mapping, mapping_val in config.get("folder_mappings", {}).items():
        if not isinstance(mapping, str) or not mapping.strip():
            raise ValueError("Folder mapping name is not a non-empty string.")

        if not isinstance(mapping_val, str) or not mapping_val.strip():
            raise ValueError("Mapped category name is not a non-empty string.")

        if mapping_val not in config["categories"]:
            raise ValueError("Mapped folder doesn't match a category")