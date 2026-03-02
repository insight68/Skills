#!/usr/bin/env python3
"""
Network security scanner for detecting unsafe network operations.
"""

import os
import re
from pathlib import Path
from typing import List
from models import Finding, Severity, Category


class NetworkScanner:
    """Scan for unsafe network operations in skill scripts."""

    # Patterns for detecting network requests
    NETWORK_PATTERNS = [
        r"requests\.(get|post|put|delete|patch|request)\(",
        r"urllib\.request\.",
        r"urlopen\(",
        r"fetch\(",
        r"http\.request\(",
        r"https\.request\(",
        r"axios\.(get|post|put|delete)\(",
    ]

    # Patterns for rate limiting
    RATE_LIMIT_PATTERNS = [
        r"rate[_-]?limit",
        r"ratelimit",
        r"time\.sleep\(",
        r"asyncio\.sleep\(",
        r"backoff",
        r"retry",
        r"throttle",
    ]

    # Patterns that indicate timeout is present
    TIMEOUT_PATTERNS = [
        r"timeout\s*=",
        r"timeout:",
    ]

    # Binary patterns for HTTP tools
    HTTP_BINARIES = ["curl", "wget", "http", "httpie", "httpie-go"]

    def scan_skill(self, skill_path: str, skill_name: str) -> List[Finding]:
        """Scan a skill for network security issues."""
        findings = []
        skill_dir = Path(skill_path)

        # Find all script files
        script_files = []
        for ext in [".py", ".sh", ".js"]:
            script_files.extend(skill_dir.rglob(f"scripts/*{ext}"))

        for script_file in script_files:
            try:
                content = script_file.read_text()
                findings.extend(self._scan_file(script_file, content, skill_name))
            except Exception:
                continue

        return findings

    def _scan_file(self, file_path: Path, content: str, skill_name: str) -> List[Finding]:
        """Scan a single file for network security issues."""
        findings = []
        lines = content.split("\n")

        # Check for unencrypted HTTP
        findings.extend(self._check_unencrypted_http(file_path, content, lines, skill_name))

        # Check for missing rate limiting
        findings.extend(self._check_rate_limiting(file_path, content, lines, skill_name))

        # Check for missing timeout
        findings.extend(self._check_timeout(file_path, content, lines, skill_name))

        # Check for URL injection
        findings.extend(self._check_url_injection(file_path, content, lines, skill_name))

        return findings

    def _check_unencrypted_http(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for unencrypted HTTP URLs."""
        findings = []

        # Pattern for http:// URLs (but not https://)
        # Exclude markdown links and comments
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue

            # Look for http:// (not https://)
            matches = re.finditer(r'http://["\']?[^"\s\]', line)
            for match in matches:
                findings.append(Finding(
                    rule_id="NET-001",
                    severity=Severity.HIGH,
                    category=Category.NETWORK_SAFETY,
                    title="Unencrypted HTTP detected",
                    description="Unencrypted HTTP traffic can be intercepted and modified. Use HTTPS only.",
                    location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                    evidence=line.strip(),
                    remediation="Replace 'http://' with 'https://' for encrypted communication.",
                    references=["https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html"],
                    cwe="CWE-319",
                ))

        return findings

    def _check_rate_limiting(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for missing rate limiting on API calls."""
        findings = []

        # First check if there are network requests
        has_network = any(re.search(pattern, content) for pattern in self.NETWORK_PATTERNS)
        has_http_binary = any(binary in content for binary in self.HTTP_BINARIES)

        if not (has_network or has_http_binary):
            return []

        # Check if rate limiting is implemented
        has_rate_limit = any(re.search(pattern, content, re.IGNORECASE) for pattern in self.RATE_LIMIT_PATTERNS)

        if not has_rate_limit:
            findings.append(Finding(
                rule_id="NET-002",
                severity=Severity.MEDIUM,
                category=Category.NETWORK_SAFETY,
                title="Missing rate limiting on external API calls",
                description="External API calls without rate limiting can overwhelm the target service or lead to IP bans.",
                location=str(file_path.relative_to(file_path.parents[2])),
                evidence="Network requests detected without rate limiting mechanism.",
                remediation="Implement rate limiting with exponential backoff. Example:\nimport time\nimport random\n\ndef fetch_with_backoff(url, max_retries=3):\n    for attempt in range(max_retries):\n        try:\n            response = requests.get(url)\n            time.sleep(1 + attempt * 2)  # Exponential backoff\n            return response\n        except Exception:\n            if attempt == max_retries - 1:\n                raise\n            time.sleep(2 ** attempt + random.uniform(0, 1))",
                references=["https://cloud.google.com/architecture/rate-limiting-strategies-techniques"],
            ))

        return findings

    def _check_timeout(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for missing timeout on network requests."""
        findings = []

        # Look for network requests without timeout
        for i, line in enumerate(lines, 1):
            # Check for requests calls
            requests_match = re.search(r'requests\.(get|post|put|delete|patch|request)\s*\([^)]*\)', line)
            if requests_match:
                call_content = requests_match.group(0)
                if not any(re.search(pattern, call_content) for pattern in self.TIMEOUT_PATTERNS):
                    findings.append(Finding(
                        rule_id="NET-003",
                        severity=Severity.MEDIUM,
                        category=Category.NETWORK_SAFETY,
                        title="Network request without timeout",
                        description="Network requests without timeout can hang indefinitely if the server is unresponsive.",
                        location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                        evidence=line.strip(),
                        remediation="Add timeout parameter to requests. Example:\nrequests.get(url, timeout=30)  # 30 second timeout",
                        references=["https://requests.readthedocs.io/en/latest/user/advanced/#timeouts"],
                    ))

            # Check for urllib without timeout
            urllib_match = re.search(r'urllib\.request\.(urlopen|Request)\s*\([^)]*\)', line)
            if urllib_match:
                call_content = urllib_match.group(0)
                if "timeout" not in call_content:
                    findings.append(Finding(
                        rule_id="NET-003",
                        severity=Severity.MEDIUM,
                        category=Category.NETWORK_SAFETY,
                        title="urllib request without timeout",
                        description="urllib requests without timeout can hang indefinitely if the server is unresponsive.",
                        location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                        evidence=line.strip(),
                        remediation="Add timeout parameter. Example:\nurllib.request.urlopen(url, timeout=30)",
                        references=["https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen"],
                    ))

        return findings

    def _check_url_injection(self, file_path: Path, content: str, lines: List[str], skill_name: str) -> List[Finding]:
        """Check for potential URL injection vulnerabilities."""
        findings = []

        # Patterns that might indicate user-controlled URLs
        user_input_patterns = [
            r"sys\.argv",
            r"input\(",
            r"args\.",
            r"user_input",
            r"user_url",
            r"target_url",
        ]

        for i, line in enumerate(lines, 1):
            # Check if network request uses potentially user-controlled input
            for pattern in self.NETWORK_PATTERNS:
                if re.search(pattern, line):
                    # Check if URL comes from user input
                    for input_pattern in user_input_patterns:
                        if re.search(input_pattern, line):
                            findings.append(Finding(
                                rule_id="NET-004",
                                severity=Severity.CRITICAL,
                                category=Category.NETWORK_SAFETY,
                                title="Potential URL injection vulnerability",
                                description="User-controlled URL in network request without validation can lead to Server-Side Request Forgery (SSRF) attacks.",
                                location=f"{file_path.relative_to(file_path.parents[2])}:{i}",
                                evidence=line.strip(),
                                remediation="Validate URLs against a whitelist before making requests. Example:\nfrom urllib.parse import urlparse\n\nALLOWED_DOMAINS = ['api.example.com']\n\ndef is_valid_url(url):\n    parsed = urlparse(url)\n    return parsed.netloc in ALLOWED_DOMAINS and parsed.scheme == 'https'\n\nif is_valid_url(user_url):\n    response = requests.get(user_url)",
                                references=["https://owasp.org/www-community/attacks/Server_Side_Request_Forgery"],
                                cwe="CWE-918",
                            ))

        return findings
