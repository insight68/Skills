#!/usr/bin/env python3
"""
Console reporter for real-time colored output.
"""

import sys
from typing import List
from models import AuditResult, SkillReport, Finding, Severity


class ConsoleReporter:
    """Generate real-time colored console output."""

    # ANSI color codes
    COLORS = {
        "red": "\033[91m",
        "yellow": "\033[93m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self.current_skill = 0

    def _color(self, text: str, color: str) -> str:
        """Apply color to text."""
        if not sys.stdout.isatty():
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _bold(self, text: str) -> str:
        """Make text bold."""
        if not sys.stdout.isatty():
            return text
        return f"{self.COLORS['bold']}{text}{self.COLORS['reset']}"

    def generate(self, result: AuditResult) -> str:
        """Generate complete console report."""
        output = []

        # Header
        output.append(self._bold("=" * 60))
        output.append(self._bold("🔒 Skill Security Audit Report"))
        output.append(self._bold("=" * 60))
        output.append("")

        # Summary
        output.append(self._bold("📊 Summary"))
        output.append(f"   Skills scanned: {result.total_skills}")
        output.append(f"   Skills with issues: {result.skills_with_issues}")

        # Risk distribution with colors
        dist = result.risk_distribution
        crit_count = dist.get("critical", 0)
        high_count = dist.get("high", 0)
        med_count = dist.get("medium", 0)
        low_count = dist.get("low", 0)

        if crit_count > 0:
            label = f"Critical: {crit_count}"
            output.append(f"   {self._color(label, 'red')} 🔴")
        if high_count > 0:
            label = f"High: {high_count}"
            output.append(f"   {self._color(label, 'yellow')} ⚠️")
        if med_count > 0:
            label = f"Medium: {med_count}"
            output.append(f"   {self._color(label, 'cyan')} ⚡")
        if low_count > 0:
            label = f"Low: {low_count}"
            output.append(f"   {self._color(label, 'blue')} ℹ️")

        output.append("")

        # Overall score
        score = result.overall_score
        score_color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        output.append(f"   {self._bold('Overall Security Score')}: {self._color(f'{score}/100', score_color)}")
        output.append("")

        # Skills with critical findings
        critical_skills = [s for s in result.skills if any(f.severity == Severity.CRITICAL for f in s.findings)]
        if critical_skills:
            output.append(self._bold("🚨 Critical Issues"))
            output.append("")

            for skill in critical_skills:
                output.append(f"   {self._color(skill.name, 'red')}")
                for finding in skill.findings:
                    if finding.severity == Severity.CRITICAL:
                        output.append(f"     {finding.icon} {finding.rule_id}: {finding.title}")
                        output.append(f"       Location: {finding.location}")
                        output.append("")

        # Skills with high findings
        high_skills = [s for s in result.skills if any(f.severity == Severity.HIGH for f in s.findings)
                       and not any(f.severity == Severity.CRITICAL for f in s.findings)]
        if high_skills:
            output.append(self._bold("⚠️  High Priority Issues"))
            output.append("")

            for skill in high_skills[:10]:  # Limit to 10
                output.append(f"   {self._color(skill.name, 'yellow')}")
                high_findings = [f for f in skill.findings if f.severity == Severity.HIGH]
                for finding in high_findings[:3]:  # Limit to 3 per skill
                    output.append(f"     {finding.icon} {finding.rule_id}: {finding.title}")
                if len(high_findings) > 3:
                    output.append(f"     ... and {len(high_findings) - 3} more")
                output.append("")

        # All skills with findings
        output.append(self._bold("📦 Detailed Findings"))
        output.append("")

        for skill in result.get_skills_by_risk():
            if not skill.findings:
                continue

            # Show worst findings first
            critical = skill.get_findings_by_severity(Severity.CRITICAL)
            high = skill.get_findings_by_severity(Severity.HIGH)
            medium = skill.get_findings_by_severity(Severity.MEDIUM)
            low = skill.get_findings_by_severity(Severity.LOW)

            risk_color_map = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "cyan", "SAFE": "green"}
            risk_color = risk_color_map.get(skill.risk_level, "blue")

            output.append(f"   {self._color(skill.name, risk_color)} ({skill.risk_level} Risk - Score: {skill.score}/100)")

            # Limit findings shown per skill
            for finding in (critical + high + medium + low)[:5]:
                output.append(f"     {finding.icon} {finding.rule_id}: {finding.title}")
                output.append(f"       → {finding.location}")

            if len(skill.findings) > 5:
                output.append(f"     ... and {len(skill.findings) - 5} more findings")
            output.append("")

        # Safe skills
        safe_skills = [s for s in result.skills if not s.findings]
        if safe_skills:
            output.append(self._bold(f"✅ Safe Skills ({len(safe_skills)})"))
            safe_names = ", ".join(s.name for s in safe_skills[:20])
            output.append(f"   {safe_names}")
            if len(safe_skills) > 20:
                output.append(f"   ... and {len(safe_skills) - 20} more")
            output.append("")

        return "\n".join(output)

    def progress_start(self, skill_name: str, index: int, total: int):
        """Show progress for starting a skill scan."""
        if not self.show_progress:
            return
        self.current_skill = index
        print(f"[{index}/{total}] {self._bold('Scanning')} {skill_name}...", end="\r")

    def progress_complete(self, skill_report: SkillReport):
        """Show progress result."""
        if not self.show_progress:
            return

        findings_count = len(skill_report.findings)
        if findings_count == 0:
            status = f"{self._color('✅ OK', 'green')}"
        else:
            worst = skill_report.risk_level
            color_map = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "cyan", "LOW": "blue"}
            icon_map = {"CRITICAL": "🔴", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "ℹ️"}
            color = color_map.get(worst, "white")
            icon = icon_map.get(worst, "📝")
            status = f"{self._color(f'{icon} {findings_count} findings', color)}"

        print(f"[{self.current_skill}/?] {skill_report.name}: {status}  ")

    def progress_done(self):
        """Clear progress line."""
        if not self.show_progress:
            return
        print(" " * 80, end="\r")
