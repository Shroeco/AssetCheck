from pathlib import Path
from assetcheck.models import ScannedFile, ValidationIssue, Severity

def validate_files(scanned_files: list[ScannedFile], file_categories: dict[Path, str], category_extensions: dict[str, list[str]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for file in scanned_files:
        extension = file.extension
        category = file_categories.get(file.path)
        
        if category is None:
            continue

        allowed_extensions = category_extensions.get(category)

        if allowed_extensions is None:
            continue

        if any(extension.lower() == allowed.lower() for allowed in allowed_extensions):
            continue
        elif not any(extension.lower() == allowed.lower() for extensions in category_extensions.values() for allowed in extensions):
            issues_file = ValidationIssue(file.path, "extension_check", Severity.INFO, "File extension is not configured for categorisation.", None, extension)
            issues.append(issues_file)
        else:
            issues_file = ValidationIssue(file.path, "extension_check", Severity.WARNING, "File extension is not permitted for this category.", ", ".join(allowed_extensions), extension)
            issues.append(issues_file)


    return issues