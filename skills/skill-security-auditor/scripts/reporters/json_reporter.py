#!/usr/bin/env python3
"""
JSON reporter for machine-readable output.
"""

from models import AuditResult


class JsonReporter:
    """Generate machine-readable JSON output."""

    def generate(self, result: AuditResult) -> dict:
        """Generate complete JSON report."""
        return result.to_dict()

    def generate_string(self, result: AuditResult, indent: int = 2) -> str:
        """Generate JSON string."""
        import json
        return json.dumps(self.generate(result), indent=indent, ensure_ascii=False)
