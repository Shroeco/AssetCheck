from pathlib import Path
from assetcheck.models import ScanResult, ScanError, ScannedFile

def scan_directory(directory: Path) -> ScanResult:
    if not (directory.exists()):
        raise FileNotFoundError("The directory does not exist.")

    if not (directory.is_dir()):
        raise NotADirectoryError("This isn't a directory.")

    scanned_files = []
    errors = []

    _scan_directory_contents(directory, scanned_files, errors)

    return ScanResult(scanned_files, errors)

def _scan_directory_contents(directory: Path, scanned_files: list[ScannedFile], errors: list[ScanError]) -> None:
    try:
        for entry in directory.iterdir():
            try:
                is_symlink = entry.is_symlink() 
                if not is_symlink:
                    is_dir = entry.is_dir()
                    is_file = entry.is_file()

                    if is_dir:
                        #iterating
                        _scan_directory_contents(entry, scanned_files, errors)
                    elif is_file:
                        #scanning files
                        scanned_file = ScannedFile(entry, entry.stat().st_size)
                        scanned_files.append(scanned_file)
            except OSError as exc:
                scanned_error = ScanError(entry, str(exc))
                errors.append(scanned_error)
    except OSError as exc:
        scanned_error = ScanError(directory, str(exc))
        errors.append(scanned_error)