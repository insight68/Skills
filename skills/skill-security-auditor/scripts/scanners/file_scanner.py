#!/usr/bin/env python3
"""
File operation scanner for detecting unsafe file system operations.
"""

import os
import re
from pathlib import Path
from typing import List
from models import Finding, Severity, Category


class FileScanner:
    """Scan for unsafe file system operations."""

    # Unsafe permission patterns
    UNSAFE_PERMISSIONS = [
        (r"chmod\s*\(\s*0o777", "0o777"),
        (r"chmod\s*\(\s*0o666", "0o666"),
        (r"chmod\s*\(\s*0o777", "0777"),
        (r"chmod\s*\(\s*0o666", "0666"),
        (r"0o777", "0o777"),
        (r"0o666", "0o666"),
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"open\s*\(\s*[^,)]*\+[^,)]*\)",  # open with concatenation
        r"Path\s*\(\s*[^)]*\+[^)]*\)",  # Path with concatenation
        r"os\.path\.join\s*\(\s*[^,)]*,\s*[^)]*\+[^)]*\)",  # join with concatenation
        r'\.\./',  # literal ../
        r'\.\.\\',  # literal ..\
    ]

    # File write patterns
    FILE_WRITE_PATTERNS = [
        r"\.write\(",
        r"\.write_text\(",
        r"open\s*\([^)]*['\"]w['\"]",
        r"open\s*\([^)]*['\"]a['\"]",
    ]

    def scan_skill(self, skill_path: str, skill_name: str) -> List[Finding]:
        """Scan a skill for file operation security issues."""
        findings = []
        skill_dir = Path(skill_path)

        # Find all script files
        script_files = []
        for ext in [".py", ".sh", ".js"]:
            script_files.extend(skill_dir.rglob(f"scripts/*{ext}"))

        for script_file in script_files:
            try:
                content = script_file.read_text()
                lines = content.split("\n")
                findings.extend(self._scan_file(script_file, content, lines, skill_name))
            except Exception:
                continue

        return findings

    def _scan_file(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Scan a single file for file operation issues."""
        findings = []

        # Check for unsafe permissions
        findings.extend(self._check_unsafe_permissions(file_path, content, lines, skill_name))

        # Check for path traversal
        findings.extend(self._check_path_traversal(file_path, content, lines, skill_name))

        return findings

    def _check_unsafe_permissions(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for unsafe file permissions."""
        findings = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue

            # Check for unsafe permission patterns
            for pattern, perm in self.UNSAFE_PERMISSIONS:
                if re.search(pattern, line):
                    findings.append(Finding(
                        rule_id="FILE-002",
                        severity=Severity.MEDIUM,
                        category=Category.FILE_OPERATIONS,
                        title=f"Unsafe file permissions: {perm}",
                        description=f"File permission {perm} is excessively permissive. Files should have minimum required permissions.",
                        location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                        evidence=line.strip(),
                        remediation=f"Use minimum required permissions:\n- For private files: 0o600 (read/write for owner only)\n- For private directories: 0o700 (rwx for owner only)\n- For shared files: 0o640 (read/write for owner, read for group)\n\nExample:\nPath(file).chmod(0o600)  # Private file\nPath(dir).chmod(0o700)  # Private directory",
                        references=["https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html"],
                        cwe="CWE-732",
                    ))

        return findings

    def _check_path_traversal(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for potential path traversal vulnerabilities."""
        findings = []

        # User input indicators
        user_input_patterns = [
            r"sys\.argv",
            r"input\(",
            r"args\.",
            r"user_input",
            r"filename",
            r"filepath",
        ]

        for i, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue

            # Check for path traversal patterns with user input
            for input_pattern in user_input_patterns:
                if re.search(input_pattern, line):
                    # Check if used in file operations
                    for traversal_pattern in self.PATH_TRAVERSAL_PATTERNS:
                        if re.search(traversal_pattern, line):
                            findings.append(Finding(
                                rule_id="FILE-001",
                                severity=Severity.CRITICAL,
                                category=Category.FILE_OPERATIONS,
                                title="Potential path traversal vulnerability",
                                description="User input used in file path without validation can lead to path traversal attacks, allowing access to arbitrary files.",
                                location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                                evidence=line.strip(),
                                remediation="Validate and sanitize file paths:\nimport os\nfrom pathlib import Path\n\ndef safe_path(base_dir: str, user_path: str) -> Path:\n    # Resolve the full path\n    full_path = (Path(base_dir) / user_path).resolve()\n    base_resolved = Path(base_dir).resolve()\n    \n    # Ensure the path is within base directory\n    if not str(full_path).startswith(str(base_resolved)):\n        raise ValueError(\"Path traversal detected\")\n    \n    return full_path\n\n# Usage\nsafe_file = safe_path('/app/uploads', user_filename)",
                                references=["https://owasp.org/www-community/attacks/Path_Traversal"],
                                cwe="CWE-22",
                            ))

            # Also check for literal ../ patterns (could be accidental)
            if re.search(r'\.\./', line) or re.search(r'\.\.\\', line):
                # Only warn if not obviously safe
                if not any(safe in line for safe in ["os.path.normpath", "resolve", "sanitize"]):
                    findings.append(Finding(
                        rule_id="FILE-001",
                        severity=Severity.MEDIUM,
                        category=Category.FILE_OPERATIONS,
                        title="Potential path traversal with literal '../'",
                        description="Literal '../' in file paths could indicate path traversal vulnerability or unsafe path handling.",
                        location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                        evidence=line.strip(),
                        remediation="Use pathlib.Path.resolve() to normalize paths:\nfrom pathlib import Path\n\n# Safe approach\nsafe_path = Path(user_input).resolve()\nif not str(safe_path).startswith(str(allowed_dir)):\n    raise ValueError(\"Path outside allowed directory\")",
                        references=["https://owasp.org/www-community/attacks/Path_Traversal"],
                        cwe="CWE-22",
                    ))

        return findings
