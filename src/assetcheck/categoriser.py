from pathlib import Path
from assetcheck.models import ScannedFile

def categorise_files(scanned_files: list[ScannedFile], folder_mappings: dict[str, str], scan_root: Path) -> dict[Path, str]:
    categorised_files: dict[Path, str] = {}

    for file in scanned_files:
        relative_path = file.path.relative_to(scan_root)
        file_parts = relative_path.parent.parts

        deepest_match = None
        deepest_match_length = 0
        matched_category = None

        for folder, category in folder_mappings.items():
            folder_parts = Path(folder).parts
            folder_length = len(folder_parts)

            for i in range(len(file_parts) - folder_length + 1):
                if file_parts[i:i + folder_length] == folder_parts:

                    if folder_length > deepest_match_length:
                        deepest_match = folder
                        deepest_match_length = folder_length
                        matched_category = category

        if matched_category is not None:
            categorised_files[file.path] = matched_category

    return categorised_files
