# AssetCheck

AssetCheck is a configurable desktop application for scanning game asset directories, categorising files, and checking whether their file extensions are permitted for their assigned categories.

## Features

- **Directory scanning** – Scan a selected directory and collect file information.
- **Configurable categorisation** – Assign files to categories using folder-based mappings.
- **Nested folder support** – More specific folder mappings take priority over broader mappings.
- **Extension validation** – Check files against the allowed extensions for their assigned categories.
- **Results overview** – View scan results, validation issues, and file details in a desktop interface.
- **Configurable rules** – Define categories, extensions, and folder mappings in a JSON configuration file.

## Requirements

- Python 3.11 or later

## Installation

Clone the repository:

```bash
git clone https://github.com/Shroeco/AssetCheck.gi
cd AssetCheck
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project:

```bash
python -m pip install .
```

For development, install the project in editable mode instead:

```bash
python -m pip install -e .
```

## Running the application

Launch AssetCheck with:

```bash
python -m assetcheck.main
```

## Configuration

AssetCheck uses a JSON configuration file located at:

```text
src/assetcheck/default_config.json
```

The configuration defines the available categories, their permitted file extensions, and the folder mappings used to categorise scanned files.

Example:

```json
{
    "categories": {
        "Textures": {
            "extensions": [".png", ".jpg", ".jpeg", ".tga"]
        },
        "Audio": {
            "extensions": [".wav", ".ogg", ".mp3"]
        },
        "Models": {
            "extensions": [".fbx", ".obj"]
        }
    },
    "folder_mappings": {
        "Textures": "Textures",
        "Audio": "Audio",
        "Models": "Models"
    }
}
```

### Folder mappings

Folder mappings associate folder paths with category names.

For example:

```json
"folder_mappings": {
    "Models": "Models",
    "Models/Animations": "Animations"
}
```

Files inside `Models/Animations` will be assigned to the `Animations` category rather than the broader `Models` category.

Files that do not match a configured folder mapping remain uncategorised and are skipped during extension validation.

### Validation results

AssetCheck reports validation issues using three severity levels:

| Severity | Meaning |
|---|---|
| INFO | The file extension is not configured for categorisation. |
| WARNING | The file extension is not permitted for its assigned category. |
| ERROR | An error occurred while scanning the file or directory. |

## Running tests

Run the test suite from the project root:

```bash
python -m pytest
```

## Project status

AssetCheck is currently a development project. Its initial functionality covers directory scanning, configurable folder-based categorisation, extension validation, and displaying results through a desktop interface.