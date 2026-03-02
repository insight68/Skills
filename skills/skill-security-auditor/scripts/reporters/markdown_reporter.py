#!/usr/bin/env python3
"""
Markdown reporter for human-readable detailed reports.
"""

from datetime import datetime
from models import AuditResult, SkillReport, Finding, Severity


class MarkdownReporter:
    """Generate detailed markdown reports."""

    def generate(self, result: AuditResult) -> str:
        """Generate complete markdown report."""
        lines = []

        # Title and metadata
        lines.append("# 🔒 Skill Security Audit Report")
        lines.append("")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Scanner Version**: {result.scanner_version}")
        lines.append("")

        # Executive Summary
        lines.append("## 📊 Executive Summary")
        lines.append("")
        lines.append(f"- **Total Skills**: {result.total_skills}")
        lines.append(f"- **Skills with Issues**: {result.skills_with_issues}")
        lines.append(f"- **Overall Security Score**: {result.overall_score}/100")
        lines.append("")

        # Risk Distribution Table
        dist = result.risk_distribution
        lines.append("### Risk Distribution")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        if dist["critical"] > 0:
            lines.append(f"| 🔴 CRITICAL | {dist['critical']} |")
        if dist["high"] > 0:
            lines.append(f"| ⚠️ HIGH | {dist['high']} |")
        if dist["medium"] > 0:
            lines.append(f"| ⚡ MEDIUM | {dist['medium']} |")
        if dist["low"] > 0:
            lines.append(f"| ℹ️ LOW | {dist['low']} |")
        if dist["info"] > 0:
            lines.append(f"| 📝 INFO | {dist['info']} |")
        lines.append("")

        # Critical Findings Section
        critical_findings = [f for f in result.all_findings if f.severity == Severity.CRITICAL]
        if critical_findings:
            lines.append("## 🚨 Critical Findings")
            lines.append("")
            lines.append("_These issues require immediate attention._")
            lines.append("")

            # Group by skill
            by_skill = {}
            for finding in critical_findings:
                for skill in result.skills:
                    if finding in skill.findings:
                        by_skill.setdefault(skill.name, []).append(finding)
                        break

            for skill_name, findings in by_skill.items():
                lines.append(f"### {skill_name}")
                lines.append("")
                for finding in findings:
                    lines.append(f"#### {finding.rule_id}: {finding.title}")
                    lines.append("")
                    lines.append(f"- **Severity**: 🔴 CRITICAL")
                    lines.append(f"- **Location**: `{finding.location}`")
                    lines.append(f"- **Category**: {finding.category.value}")
                    if finding.cwe:
                        lines.append(f"- **CWE**: {finding.cwe}")
                    lines.append("")
                    lines.append(f"**Description**: {finding.description}")
                    lines.append("")
                    lines.append("**Evidence**:")
                    lines.append("```")
                    lines.append(finding.evidence)
                    lines.append("```")
                    lines.append("")
                    lines.append("**Remediation**:")
                    lines.append("```python")
                    lines.append(finding.remediation)
                    lines.append("```")
                    if finding.references:
                        lines.append("**References**:")
                        for ref in finding.references:
                            lines.append(f"- [{ref}]({ref})")
                        lines.append("")
                    lines.append("")

        # High Priority Findings
        high_findings = [f for f in result.all_findings if f.severity == Severity.HIGH]
        if high_findings:
            lines.append("## ⚠️ High Priority Findings")
            lines.append("")
            lines.append("_These issues should be addressed soon._")
            lines.append("")

            for finding in high_findings[:20]:  # Limit to 20
                skill_name = next((s.name for s in result.skills if finding in s.findings), "Unknown")
                lines.append(f"### {skill_name}: {finding.rule_id}")
                lines.append("")
                lines.append(f"**{finding.title}**")
                lines.append("")
                lines.append(f"- **Location**: `{finding.location}`")
                lines.append(f"- **Description**: {finding.description}")
                lines.append("")
                lines.append("**Fix**:")
                lines.append("```python")
                lines.append(finding.remediation[:500])  # Limit length
                if len(finding.remediation) > 500:
                    lines.append("... (truncated)")
                lines.append("```")
                lines.append("")

            if len(high_findings) > 20:
                lines.append(f"_... and {len(high_findings) - 20} more high priority findings_")
                lines.append("")

        # Detailed Findings by Skill
        lines.append("## 📦 Detailed Findings by Skill")
        lines.append("")

        for skill in result.get_skills_by_risk():
            if not skill.findings:
                continue

            lines.append(f"### {skill.name} ({skill.risk_level} Risk - Score: {skill.score}/100)")
            lines.append("")

            # Group findings by severity
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                findings = skill.get_findings_by_severity(severity)
                if findings:
                    icon = severity.icon()
                    lines.append(f"#### {severity.value} ({len(findings)})")
                    lines.append("")

                    for finding in findings:
                        lines.append(f"**{finding.rule_id}**: {finding.title}")
                        lines.append(f"- Location: `{finding.location}`")
                        lines.append(f"- {finding.description}")
                        lines.append("")

        # Safe Skills
        safe_skills = [s for s in result.skills if not s.findings]
        if safe_skills:
            lines.append(f"## ✅ Safe Skills ({len(safe_skills)})")
            lines.append("")
            lines.append("The following skills have no security findings:")
            lines.append("")
            for skill in safe_skills:
                lines.append(f"- **{skill.name}** - Score: 100/100")
            lines.append("")

        # Recommendations
        lines.append("## 💡 Recommendations")
        lines.append("")

        if result.critical_count > 0:
            lines.append("1. **🚨 Immediate Actions**: Fix all CRITICAL issues within 7 days")
        if result.high_count > 0:
            lines.append(f"2. **⚠️ Short Term**: Address HIGH issues within 30 days ({result.high_count} issues)")
        if result.medium_count > 0:
            lines.append(f"3. **⚡ Medium Term**: Implement MEDIUM findings in next quarterly cycle ({result.medium_count} issues)")
        if result.low_count > 0:
            lines.append(f"4. **ℹ️ Long Term**: Review LOW findings for improvement opportunities ({result.low_count} issues)")
        lines.append("")

        # Security Best Practices
        lines.append("## 📚 Security Best Practices")
        lines.append("")
        lines.append("- **Network Security**: Always use HTTPS, implement rate limiting, add timeouts")
        lines.append("- **File Operations**: Validate paths, use minimum permissions, check file types")
        lines.append("- **Command Execution**: Use list arguments, avoid shell=True, validate input")
        lines.append("- **Permissions**: Declare all requirements, use principle of least privilege")
        lines.append("- **Error Handling**: Fail gracefully, log security events, don't expose internals")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"_Generated by [skill-security-auditor](https://github.com/anthropics/agent-skills) v{result.scanner_version}_")
        lines.append("")

        return "\n".join(lines)
