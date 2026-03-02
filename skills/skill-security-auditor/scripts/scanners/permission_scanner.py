#!/usr/bin/env python3
"""
Permission validation scanner for cross-checking declared permissions against actual usage.
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Set, Tuple
from models import Finding, Severity, Category


class PermissionScanner:
    """Scan for permission declaration issues."""

    # Environment variable access patterns
    ENV_PATTERNS = [
        r"os\.environ\[",
        r"os\.getenv\(",
        r"os\.getenv\(",
        r"environ\.get\(",
        r'\$\{[A-Z_]+\}',  # Shell ${VAR} pattern
        r'\$[A-Z_]+',  # Shell $VAR pattern
    ]

    # Subprocess/binary execution patterns
    BINARY_PATTERNS = [
        r"subprocess\.\w+\(\s*\[",
        r"subprocess\.call",
        r"subprocess\.run",
        r"subprocess\.Popen",
        r"os\.system\(",
        r"os\.popen\(",
        r"popen\(",
    ]

    # Common binary names to look for
    COMMON_BINARIES = [
        "git", "curl", "wget", "jq", "tmux", "ffmpeg", "convert", "ffprobe",
        "node", "npm", "pnpm", "yarn", "python", "python3", "ruby", "go",
        "docker", "kubectl", "aws", "gcloud", "az",
        "convert", "identify", "composite",  # ImageMagick
        "ffmpeg", "ffprobe",
    ]

    def scan_skill(self, skill_path: str, skill_name: str, frontmatter: dict) -> List[Finding]:
        """Scan a skill for permission validation issues."""
        findings = []
        skill_dir = Path(skill_path)

        # Extract declared permissions from frontmatter
        declared_env, declared_bins = self._parse_declared_permissions(frontmatter)

        # Scan for actual usage in scripts
        used_env, used_bins = self._scan_actual_usage(skill_dir)

        # Cross-check for undeclared usage
        findings.extend(self._check_undeclared_env(
            skill_name, skill_dir, declared_env, used_env
        ))

        findings.extend(self._check_undeclared_bins(
            skill_name, skill_dir, declared_bins, used_bins
        ))

        # Check for unused declarations (lower priority)
        findings.extend(self._check_unused_env(
            skill_name, declared_env, used_env
        ))

        findings.extend(self._check_unused_bins(
            skill_name, declared_bins, used_bins
        ))

        return findings

    def _parse_declared_permissions(self, frontmatter: dict) -> Tuple[Set[str], Set[str]]:
        """Parse declared permissions from YAML frontmatter."""
        declared_env = set()
        declared_bins = set()

        # Check for openclaw metadata format (from trello/SKILL.md pattern)
        metadata = frontmatter.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = yaml.safe_load(metadata)
            except:
                metadata = {}

        openclaw = metadata.get("openclaw", {}) if metadata else {}
        requires = openclaw.get("requires", {}) if openclaw else {}

        # Get environment variables
        if isinstance(requires, dict):
            env_list = requires.get("env", [])
            if env_list:
                declared_env.update(env_list if isinstance(env_list, list) else [env_list])

            # Get binary dependencies
            bins_list = requires.get("bins", [])
            if bins_list:
                declared_bins.update(bins_list if isinstance(bins_list, list) else [bins_list])

        # Also check for direct requires field
        if isinstance(requires, dict):
            env_list = requires.get("env", [])
            if env_list:
                declared_env.update(env_list if isinstance(env_list, list) else [env_list])

            bins_list = requires.get("bins", [])
            if bins_list:
                declared_bins.update(bins_list if isinstance(bins_list, list) else [bins_list])

        return declared_env, declared_bins

    def _scan_actual_usage(self, skill_dir: Path) -> Tuple[Set[str], Dict[str, List[str]]]:
        """Scan scripts for actual environment variable and binary usage."""
        used_env = set()
        used_bins = {}  # binary -> list of locations

        # Find all script files
        for script_file in skill_dir.rglob("scripts/*"):
            if script_file.suffix not in [".py", ".sh", ".js"]:
                continue

            try:
                content = script_file.read_text()
                lines = content.split("\n")

                # Scan for environment variables
                for i, line in enumerate(lines, 1):
                    # Python patterns
                    matches = re.findall(r'os\.environ\[["\']([^"\']+)["\']\]', line)
                    for match in matches:
                        used_env.add(match)
                        used_env.setdefault(match, []).append(f"{script_file.name}:{i}")

                    matches = re.findall(r'os\.getenv\(["\']([^"\']+)["\']\]', line)
                    for match in matches:
                        used_env.add(match)
                        used_env.setdefault(match, []).append(f"{script_file.name}:{i}")

                    # Shell patterns
                    shell_matches = re.findall(r'\$\{([A-Z_][A-Z0-9_]*)\}', line)
                    for match in shell_matches:
                        used_env.add(match)

                    shell_matches = re.findall(r'\$([A-Z_][A-Z0-9_]*)\b', line)
                    for match in shell_matches:
                        # Exclude shell builtins and common variables
                        if match not in ["PATH", "HOME", "USER", "SHELL", "PWD"]:
                            used_env.add(match)

                # Scan for binary usage in subprocess calls
                for i, line in enumerate(lines, 1):
                    # Python subprocess with list args
                    matches = re.findall(r'subprocess\.\w+\(\s*\[\s*["\']([\w\-]+)', line)
                    for match in matches:
                        if match in self.COMMON_BINARIES:
                            used_bins.setdefault(match, []).append(f"{script_file.name}:{i}")

                    # Shell commands (look for common binary names)
                    for binary in self.COMMON_BINARIES:
                        if re.search(rf'\b{re.escape(binary)}\b', line):
                            # Make sure it's not in a string/comment
                            if not (line.strip().startswith("#") or line.strip().startswith("//")):
                                used_bins.setdefault(binary, []).append(f"{script_file.name}:{i}")

            except Exception:
                continue

        return used_env, used_bins

    def _check_undeclared_env(
        self,
        skill_name: str,
        skill_dir: Path,
        declared_env: Set[str],
        used_env: Set[str]
    ) -> List[Finding]:
        """Check for environment variables used but not declared."""
        findings = []

        # Filter out common system variables
        system_vars = {"PATH", "HOME", "USER", "SHELL", "PWD", "TERM", "LANG"}
        undeclared = used_env - declared_env - system_vars

        if undeclared:
            findings.append(Finding(
                rule_id="PERM-001",
                severity=Severity.HIGH,
                category=Category.PERMISSION_VALIDATION,
                title=f"Undeclared environment variables: {', '.join(sorted(undeclared))}",
                description=f"The following environment variables are used in scripts but not declared in SKILL.md frontmatter: {', '.join(sorted(undeclared))}. Users need to know what environment variables to set.",
                location=f"{skill_name}/SKILL.md",
                evidence=f"Used but not declared: {', '.join(sorted(undeclared))}",
                remediation=f"Add to metadata.requires.env in SKILL.md frontmatter:\n---\nname: {skill_name}\ndescription: ...\nmetadata:\n  openclaw:\n    requires:\n      env: [{', '.join(sorted(undeclared))}]",
                references=["https://www.anthropic.com/docs/claude-code/skills#metadata"],
            ))

        return findings

    def _check_undeclared_bins(
        self,
        skill_name: str,
        skill_dir: Path,
        declared_bins: Set[str],
        used_bins: Dict[str, List[str]]
    ) -> List[Finding]:
        """Check for binaries used but not declared."""
        findings = []

        undeclared = set(used_bins.keys()) - declared_bins

        if undeclared:
            locations = ", ".join(f"{bin} ({used_bins[bin][0]})" for bin in sorted(undeclared))
            findings.append(Finding(
                rule_id="PERM-002",
                severity=Severity.MEDIUM,
                category=Category.PERMISSION_VALIDATION,
                title=f"Undeclared binary dependencies: {', '.join(sorted(undeclared))}",
                description=f"The following external binaries are used but not declared: {', '.join(sorted(undeclared))}. Users need to install these dependencies.",
                location=f"{skill_name}/SKILL.md",
                evidence=f"Used at: {locations}",
                remediation=f"Add to metadata.requires.bins in SKILL.md frontmatter:\n---\nname: {skill_name}\ndescription: ...\nmetadata:\n  openclaw:\n    requires:\n      bins: [{', '.join(sorted(undeclared))}]",
                references=["https://www.anthropic.com/docs/claude-code/skills#metadata"],
            ))

        return findings

    def _check_unused_env(
        self,
        skill_name: str,
        declared_env: Set[str],
        used_env: Set[str]
    ) -> List[Finding]:
        """Check for environment variables declared but never used."""
        findings = []

        unused = declared_env - used_env
        if unused:
            findings.append(Finding(
                rule_id="PERM-003",
                severity=Severity.LOW,
                category=Category.PERMISSION_VALIDATION,
                title=f"Unused environment variables declared: {', '.join(sorted(unused))}",
                description=f"The following environment variables are declared but never used in scripts: {', '.join(sorted(unused))}. This may confuse users.",
                location=f"{skill_name}/SKILL.md",
                evidence=f"Declared but unused: {', '.join(sorted(unused))}",
                remediation=f"Remove unused variables from metadata.requires.env:\n---\nmetadata:\n  openclaw:\n    requires:\n      env: [{', '.join(sorted(declared_env - unused))}]",
            ))

        return findings

    def _check_unused_bins(
        self,
        skill_name: str,
        declared_bins: Set[str],
        used_bins: Dict[str, List[str]]
    ) -> List[Finding]:
        """Check for binaries declared but never used."""
        findings = []

        unused = declared_bins - set(used_bins.keys())
        if unused:
            findings.append(Finding(
                rule_id="PERM-003",
                severity=Severity.LOW,
                category=Category.PERMISSION_VALIDATION,
                title=f"Unused binary dependencies declared: {', '.join(sorted(unused))}",
                description=f"The following binaries are declared but never used in scripts: {', '.join(sorted(unused))}. This may confuse users.",
                location=f"{skill_name}/SKILL.md",
                evidence=f"Declared but unused: {', '.join(sorted(unused))}",
                remediation=f"Remove unused binaries from metadata.requires.bins:\n---\nmetadata:\n  openclaw:\n    requires:\n      bins: [{', '.join(sorted(declared_bins - unused))}]",
            ))

        return findings
