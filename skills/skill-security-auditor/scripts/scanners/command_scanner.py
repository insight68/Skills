#!/usr/bin/env python3
"""
Command execution scanner for detecting unsafe command execution patterns.
"""

import os
import re
from pathlib import Path
from typing import List
from models import Finding, Severity, Category


class CommandScanner:
    """Scan for unsafe command execution patterns."""

    # Dangerous patterns
    DANGEROUS_PATTERNS = {
        "shell=True": "shell=True allows shell injection vulnerabilities",
        "os.system(": "os.system is vulnerable to command injection",
        "eval(": "eval executes arbitrary code",
        "exec(": "exec executes arbitrary code",
        "__import__('os').system": "obfuscated system call",
    }

    # User input patterns
    USER_INPUT_PATTERNS = [
        r"sys\.argv",
        r"input\(",
        r"args\.",
        r"user_input",
        r"user_data",
    ]

    def scan_skill(self, skill_path: str, skill_name: str) -> List[Finding]:
        """Scan a skill for command execution security issues."""
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
        """Scan a single file for command execution issues."""
        findings = []

        # Check for shell=True
        findings.extend(self._check_shell_true(file_path, content, lines, skill_name))

        # Check for os.system
        findings.extend(self._check_os_system(file_path, content, lines, skill_name))

        # Check for eval/exec
        findings.extend(self._check_eval_exec(file_path, content, lines, skill_name))

        # Check for missing timeout on subprocess
        findings.extend(self._check_subprocess_timeout(file_path, content, lines, skill_name))

        return findings

    def _check_shell_true(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for shell=True in subprocess calls."""
        findings = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue

            # Look for shell=True
            if "shell=True" in line:
                # Check if it might have user input
                has_user_input = any(re.search(pattern, line) for pattern in self.USER_INPUT_PATTERNS)

                findings.append(Finding(
                    rule_id="CMD-001",
                    severity=Severity.CRITICAL if has_user_input else Severity.HIGH,
                    category=Category.COMMAND_EXECUTION,
                    title=f"shell=True detected in subprocess call{' with user input' if has_user_input else ''}",
                    description="Using shell=True in subprocess calls enables shell injection vulnerabilities. An attacker can inject arbitrary commands.",
                    location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                    evidence=line.strip(),
                    remediation="Use list arguments instead of shell=True:\n# UNSAFE:\nsubprocess.run(command_string, shell=True)\n\n# SAFE:\nsubprocess.run(['command', 'arg1', 'arg2'], check=True)\n\n# If shell features are needed, validate input:\nimport shlex\nvalidated_cmd = shlex.quote(user_input)\nsubprocess.run(['command', validated_cmd])",
                    references=["https://docs.python.org/3/library/subprocess.html#security-considerations"],
                    cwe="CWE-78",
                ))

        return findings

    def _check_os_system(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for os.system usage."""
        findings = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue

            # Look for os.system
            if "os.system(" in line:
                has_user_input = any(re.search(pattern, line) for pattern in self.USER_INPUT_PATTERNS)

                findings.append(Finding(
                    rule_id="CMD-001",
                    severity=Severity.CRITICAL if has_user_input else Severity.HIGH,
                    category=Category.COMMAND_EXECUTION,
                    title=f"os.system detected{' with user input' if has_user_input else ''}",
                    description="os.system passes the command to the shell, enabling command injection. Use subprocess with list arguments instead.",
                    location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                    evidence=line.strip(),
                    remediation="Replace os.system with subprocess:\n# UNSAFE:\nos.system(f'command {user_input}')\n\n# SAFE:\nimport subprocess\nsubprocess.run(['command', user_input], check=True)",
                    references=["https://docs.python.org/3/library/subprocess.html#replacing-os-system"],
                    cwe="CWE-78",
                ))

        return findings

    def _check_eval_exec(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for eval/exec usage."""
        findings = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue

            # Look for eval
            if re.search(r'\beval\s*\(', line):
                has_user_input = any(re.search(pattern, line) for pattern in self.USER_INPUT_PATTERNS)

                findings.append(Finding(
                    rule_id="CMD-001",
                    severity=Severity.CRITICAL if has_user_input else Severity.HIGH,
                    category=Category.COMMAND_EXECUTION,
                    title=f"eval() detected{' with user input' if has_user_input else ''}",
                    description="eval() executes arbitrary code, creating a remote code execution vulnerability when used with user input.",
                    location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                    evidence=line.strip(),
                    remediation="Avoid eval entirely. Use safer alternatives:\n# Instead of eval for math:\nimport ast\nresult = ast.literal_eval('2 + 2')  # Only for literals\n\n# For user input:\n# Use configuration files, parsers, or specific handlers\n# Never execute user input as code.",
                    references=["https://owasp.org/www-community/vulnerabilities/Improper Neutralization of Directives in Dynamically Evaluated Code"],
                    cwe="CWE-95",
                ))

            # Look for exec
            if re.search(r'\bexec\s*\(', line):
                has_user_input = any(re.search(pattern, line) for pattern in self.USER_INPUT_PATTERNS)

                findings.append(Finding(
                    rule_id="CMD-001",
                    severity=Severity.CRITICAL if has_user_input else Severity.HIGH,
                    category=Category.COMMAND_EXECUTION,
                    title=f"exec() detected{' with user input' if has_user_input else ''}",
                    description="exec() executes arbitrary code, creating a remote code execution vulnerability when used with user input.",
                    location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                    evidence=line.strip(),
                    remediation="Avoid exec entirely. Use safer alternatives:\n# Instead of exec for dynamic code:\nimport importlib\nmodule = importlib.import_module(module_name)\n\n# For configuration:\nimport json\nconfig = json.loads(config_string)",
                    references=["https://owasp.org/www-community/vulnerabilities/Improper Neutralization of Directives in Dynamically Evaluated Code"],
                    cwe="CWE-95",
                ))

        return findings

    def _check_subprocess_timeout(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for subprocess calls without timeout."""
        findings = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue

            # Look for subprocess calls
            subprocess_match = re.search(r'subprocess\.(run|call|Popen)\s*\(', line)
            if subprocess_match:
                # Extract the function call to check for timeout
                # Get the rest of the line and a few more lines to find timeout parameter
                call_content = line
                j = i - 1
                # Look ahead a few lines
                for offset in range(min(5, len(lines) - i + 1)):
                    call_content += lines[j + offset]
                    if ")" in lines[j + offset]:
                        break

                # Check if timeout is present
                if "timeout" not in call_content:
                    findings.append(Finding(
                        rule_id="CMD-002",
                        severity=Severity.MEDIUM,
                        category=Category.COMMAND_EXECUTION,
                        title="subprocess call without timeout",
                        description="Command execution without timeout can hang indefinitely if the command doesn't complete.",
                        location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                        evidence=line.strip(),
                        remediation="Add timeout parameter to subprocess calls:\nsubprocess.run(['command', 'arg'], timeout=30, check=True)",
                        references=["https://docs.python.org/3/library/subprocess.html#subprocess.run"],
                    ))

        return findings
