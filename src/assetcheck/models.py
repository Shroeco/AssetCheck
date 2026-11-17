from dataclasses import dataclass
from pathlib import Path
from enum import Enum

@dataclass
class ScannedFile:
    path : Path
    size_bytes : int

    @property
    def name(self) -> str:
        return self.path.name
    @property
    def extension(self) -> str:
        return self.path.suffix

    def __post_init__(self):
        if (self.size_bytes < 0):
            raise ValueError("File has negative size, therefore cannot be stored.")

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationIssue:
    file_path : Path
    check_name : str
    severity : Severity
    message : str
    expected_value : str | None = None
    actual_value : str | None = None

@dataclass
class ScanError:
    path : Path
    message : str

@dataclass
class ScanResult:
    scanned_files : list[ScannedFile]
    errors : list[ScanError]