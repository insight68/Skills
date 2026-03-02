#!/usr/bin/env python3
"""
Data models for security audit findings.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Severity(Enum):
    """Severity levels for security findings."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    def __lt__(self, other):
        """Order severities for sorting."""
        order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
        return order.index(self) < order.index(other)

    def score(self) -> int:
        """Return numeric score for risk calculation."""
        return {
            Severity.CRITICAL: 10,
            Severity.HIGH: 5,
            Severity.MEDIUM: 2,
            Severity.LOW: 1,
            Severity.INFO: 0,
        }[self]

    def icon(self) -> str:
        """Return emoji icon for display."""
        return {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "⚠️",
            Severity.MEDIUM: "⚡",
            Severity.LOW: "ℹ️",
            Severity.INFO: "📝",
        }[self]


class Category(Enum):
    """Categories of security issues."""
    NETWORK_SAFETY = "network_safety"
    FILE_OPERATIONS = "file_operations"
    COMMAND_EXECUTION = "command_execution"
    PERMISSION_VALIDATION = "permission_validation"
    SECRET_MANAGEMENT = "secret_management"
    ERROR_HANDLING = "error_handling"
    CODE_QUALITY = "code_quality"
    AUTHOR_REPUTATION = "author_reputation"


@dataclass
class Finding:
    """A single security finding."""
    rule_id: str
    severity: Severity
    category: Category
    title: str
    description: str
    location: str  # file:line or file
    evidence: str  # code snippet or context
    remediation: str
    references: List[str] = field(default_factory=list)
    cwe: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "references": self.references,
            "cwe": self.cwe,
        }

    @property
    def icon(self) -> str:
        """Return emoji icon for display."""
        # Return icon based on severity
        icons = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "⚠️",
            Severity.MEDIUM: "⚡",
            Severity.LOW: "ℹ️",
            Severity.INFO: "📝",
        }
        return icons.get(self.severity, "📝")


@dataclass
class SkillReport:
    """Security report for a single skill."""
    name: str
    path: str
    findings: List[Finding] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def risk_level(self) -> str:
        """Calculate overall risk level."""
        if not self.findings:
            return "SAFE"

        max_severity = max(f.severity for f in self.findings)
        return max_severity.value

    @property
    def score(self) -> int:
        """Calculate security score (0-100, lower is worse)."""
        if not self.findings:
            return 100

        # Subtract points based on severity
        deduction = sum(f.severity.score() for f in self.findings)
        return max(0, 100 - deduction)

    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        """Filter findings by severity."""
        return [f for f in self.findings if f.severity == severity]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "path": self.path,
            "risk_level": self.risk_level,
            "score": self.score,
            "findings_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "metadata": self.metadata,
        }


@dataclass
class AuditResult:
    """Complete security audit result."""
    skills: List[SkillReport] = field(default_factory=list)
    timestamp: str = field(default="")
    scanner_version: str = "1.0.0"

    def __post_init__(self):
        """Set timestamp on creation."""
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()

    @property
    def total_skills(self) -> int:
        """Total number of skills audited."""
        return len(self.skills)

    @property
    def skills_with_issues(self) -> int:
        """Number of skills with findings."""
        return sum(1 for s in self.skills if s.findings)

    @property
    def all_findings(self) -> List[Finding]:
        """All findings across all skills."""
        findings = []
        for skill in self.skills:
            findings.extend(skill.findings)
        return findings

    @property
    def critical_count(self) -> int:
        """Number of critical findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Number of high findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        """Number of medium findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        """Number of low findings."""
        return sum(1 for f in self.all_findings if f.severity == Severity.LOW)

    @property
    def overall_score(self) -> int:
        """Calculate overall security score."""
        if not self.skills:
            return 100

        return sum(s.score for s in self.skills) // len(self.skills)

    @property
    def risk_distribution(self) -> Dict[str, int]:
        """Get count of findings by severity."""
        return {
            "critical": self.critical_count,
            "high": self.high_count,
            "medium": self.medium_count,
            "low": self.low_count,
            "info": sum(1 for f in self.all_findings if f.severity == Severity.INFO),
        }

    def get_skills_by_risk(self) -> List[SkillReport]:
        """Get skills sorted by risk (highest first)."""
        return sorted(self.skills, key=lambda s: s.score)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": {
                "timestamp": self.timestamp,
                "version": self.scanner_version,
                "scanner": "skill-security-auditor",
            },
            "summary": {
                "total_skills": self.total_skills,
                "skills_with_issues": self.skills_with_issues,
                "risk_distribution": self.risk_distribution,
                "security_score": self.overall_score,
            },
            "skills": [s.to_dict() for s in self.skills],
            "findings": [f.to_dict() for f in self.all_findings],
        }
