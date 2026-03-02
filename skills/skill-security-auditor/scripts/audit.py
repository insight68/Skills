#!/usr/bin/env python3
"""
Skill Security Auditor - Automated security scanning for AgentSkills.

Scans skills for vulnerabilities including unsafe network requests, file operations,
command execution, API key handling, and permission declarations.

Usage:
    python audit.py <skills_directory> [options]
"""

import os
import sys
import yaml
import argparse
import concurrent.futures
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from models import AuditResult, SkillReport, Severity
from scanners.network_scanner import NetworkScanner
from scanners.permission_scanner import PermissionScanner
from scanners.file_scanner import FileScanner
from scanners.command_scanner import CommandScanner
from reporters.console_reporter import ConsoleReporter
from reporters.markdown_reporter import MarkdownReporter
from reporters.json_reporter import JsonReporter


def scan_skills(skills_root: str, specific_skill: Optional[str] = None,
                min_risk: str = "INFO", show_progress: bool = True) -> List[SkillReport]:
    """Scan all skills in the given directory."""
    skills_list = []
    skills_dir = Path(skills_root)

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_root}", file=sys.stderr)
        return []

    # Find all skill directories with SKILL.md
    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue

        skill_md = item / "SKILL.md"
        if not skill_md.exists():
            continue

        # Filter to specific skill if requested
        if specific_skill and item.name != specific_skill:
            continue

        skills_list.append(item)

    # Sort for consistent output
    skills_list.sort()

    if not skills_list:
        if specific_skill:
            print(f"Error: Skill '{specific_skill}' not found", file=sys.stderr)
        else:
            print(f"No skills found in {skills_root}")
        return []

    # Initialize scanners
    network_scanner = NetworkScanner()
    permission_scanner = PermissionScanner()
    file_scanner = FileScanner()
    command_scanner = CommandScanner()

    # Initialize reporter for progress
    console_reporter = ConsoleReporter(show_progress=show_progress)

    # Scan skills
    results = []
    min_severity = Severity[min_risk.upper()]

    for i, skill_dir in enumerate(skills_list, 1):
        skill_name = skill_dir.name
        console_reporter.progress_start(skill_name, i, len(skills_list))

        try:
            # Parse SKILL.md frontmatter
            skill_md = skill_dir / "SKILL.md"
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            parts = content.split('---')
            if len(parts) < 3:
                frontmatter = {}
            else:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                except:
                    frontmatter = {}

            # Run all scanners
            all_findings = []

            # Network security
            all_findings.extend(network_scanner.scan_skill(str(skill_dir), skill_name))

            # Permission validation
            all_findings.extend(permission_scanner.scan_skill(str(skill_dir), skill_name, frontmatter))

            # File operations
            all_findings.extend(file_scanner.scan_skill(str(skill_dir), skill_name))

            # Command execution
            all_findings.extend(command_scanner.scan_skill(str(skill_dir), skill_name))

            # Filter by minimum risk level
            # Severity order: CRITICAL(0) > HIGH(1) > MEDIUM(2) > LOW(3) > INFO(4)
            # min_risk of HIGH means include CRITICAL and HIGH
            severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
            min_index = severity_order.index(min_severity)
            filtered_findings = [f for f in all_findings if severity_order.index(f.severity) <= min_index]

            # Create skill report
            report = SkillReport(
                name=skill_name,
                path=str(skill_dir),
                findings=filtered_findings,
                metadata=frontmatter
            )
            results.append(report)

            console_reporter.progress_complete(report)

        except Exception as e:
            print(f"\nError scanning {skill_name}: {e}", file=sys.stderr)
            continue

    console_reporter.progress_done()
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit AgentSkills for security vulnerabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit all skills with console output
  python audit.py /path/to/skills

  # Audit specific skill
  python audit.py /path/to/skills --skill instagram-marketing

  # Generate markdown report
  python audit.py /path/to/skills --format markdown --output report.md

  # Only show high and critical issues
  python audit.py /path/to/skills --min-risk HIGH

  # Generate JSON for CI/CD
  python audit.py /path/to/skills --format json --output report.json
        """
    )

    parser.add_argument(
        "skills_dir",
        help="Path to skills directory"
    )

    parser.add_argument(
        "--skill",
        help="Audit only the specified skill"
    )

    parser.add_argument(
        "--format",
        choices=["console", "markdown", "json"],
        default="console",
        help="Output format (default: console)"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )

    parser.add_argument(
        "--min-risk",
        choices=["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
        default="INFO",
        help="Minimum risk level to report (default: INFO)"
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress indicators"
    )

    args = parser.parse_args()

    # Scan skills
    skills_reports = scan_skills(
        args.skills_dir,
        specific_skill=args.skill,
        min_risk=args.min_risk,
        show_progress=not args.no_progress
    )

    if not skills_reports:
        sys.exit(1)

    # Create audit result
    result = AuditResult(skills=skills_reports)

    # Generate report
    if args.format == "console":
        reporter = ConsoleReporter(show_progress=False)
        output = reporter.generate(result)

    elif args.format == "markdown":
        reporter = MarkdownReporter()
        output = reporter.generate(result)

    elif args.format == "json":
        reporter = JsonReporter()
        output = reporter.generate_string(result)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding='utf-8')
        print(f"Report written to: {args.output}")
    else:
        print(output)

    # Exit with error code if critical issues found
    if result.critical_count > 0:
        sys.exit(2)
    elif result.high_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
