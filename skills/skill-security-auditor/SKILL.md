---
name: skill-security-auditor
description: Automated security auditing tool for AgentSkills. Scan skills for vulnerabilities including unsafe network requests, file operations, command execution, API key handling, permission declarations, and error handling. Use when: (1) Auditing existing skills for security issues, (2) Reviewing third-party skills before installation, (3) Validating self-built skills before publishing, (4) Teaching security best practices
category: security
tags: ["skills-manage","security review","security auditor"]
---

# Skill Security Auditor

Automated security analysis tool for AgentSkills that detects vulnerabilities and provides actionable remediation guidance.

## Quick Start

Run security audit on all skills:

```bash
scripts/audit.py /path/to/skills
```

Audit specific skill:

```bash
scripts/audit.py /path/to/skills --skill instagram-marketing
```

Generate detailed report:

```bash
scripts/audit.py /path/to/skills --format markdown --output security-report.md
```

## Core Capabilities

### 1. Network Safety Detection

Scans for unsafe network operations:

- **Unencrypted HTTP** (NET-001): Detects `http://` usage that should be `https://`
- **Missing Rate Limiting** (NET-002): Identifies API calls without rate limiting
- **Missing Timeout** (NET-003): Finds network requests without timeout protection
- **URL Injection** (NET-004): Detects user-controlled URLs without validation

### 2. Permission Validation

Cross-checks declared permissions against actual usage:

- **Undeclared Environment Variables** (PERM-001): `os.environ` usage not in `metadata.requires.env`
- **Undeclared Binaries** (PERM-002): `subprocess` calls not in `metadata.requires.bins`
- **Unused Declarations** (PERM-003): Declared permissions never used in code

### 3. File Operation Security

Detects file system vulnerabilities:

- **Path Traversal** (FILE-001): User input in file paths without validation
- **Unsafe Permissions** (FILE-002): Excessive permissions like `0o777` or `0o666`

### 4. Command Execution Safety

Scans for dangerous command patterns:

- **Shell Injection** (CMD-001): `shell=True`, `os.system()`, `eval()`, `exec()`
- **Missing Timeout** (CMD-002): `subprocess` calls without timeout

## Usage

### Basic Commands

```bash
# Console output (default)
scripts/audit.py /path/to/skills

# Filter by risk level
scripts/audit.py /path/to/skills --min-risk HIGH

# Specific skill
scripts/audit.py /path/to/skills --skill skill-name
```

### Output Formats

```bash
# Console (real-time colored output)
scripts/audit.py /path/to/skills --format console

# Markdown report
scripts/audit.py /path/to/skills --format markdown --output report.md

# JSON for CI/CD
scripts/audit.py /path/to/skills --format json --output report.json
```

### CLI Options

| Option | Description |
|--------|-------------|
| `skills_dir` | Path to skills directory (required) |
| `--skill NAME` | Audit only specified skill |
| `--format {console,markdown,json}` | Output format (default: console) |
| `--output, -o PATH` | Output file path |
| `--min-risk {INFO,LOW,MEDIUM,HIGH,CRITICAL}` | Minimum risk level to report |
| `--no-progress` | Disable progress indicators |

## Risk Levels

| Level | Score | Description |
|-------|-------|-------------|
| 🔴 **CRITICAL** | 10 | Immediate security threat (e.g., hardcoded secrets, command injection) |
| ⚠️ **HIGH** | 5 | Serious vulnerability (e.g., unsafe HTTP, missing validation) |
| ⚡ **MEDIUM** | 2 | Security best practice violation (e.g., missing timeout, no rate limiting) |
| ℹ️ **LOW** | 1 | Minor issue or optimization opportunity |
| 📝 **INFO** | 0 | Informational finding |

## Security Rules Reference

### Network Safety

**NET-001: Unencrypted HTTP**
- **Severity**: HIGH
- **Pattern**: `http://` URLs
- **Fix**: Replace with `https://`
- **CWE**: CWE-319

**NET-002: Missing Rate Limiting**
- **Severity**: MEDIUM
- **Pattern**: API calls without rate limiting mechanism
- **Fix**: Implement exponential backoff
- **References**: [Cloud Rate Limiting Strategies](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

**NET-003: Missing Timeout**
- **Severity**: MEDIUM
- **Pattern**: Network requests without `timeout` parameter
- **Fix**: Add `timeout=30` to requests

**NET-004: URL Injection**
- **Severity**: CRITICAL
- **Pattern**: User-controlled URL in network request
- **Fix**: Validate against whitelist, use `urlparse`
- **CWE**: CWE-918 (SSRF)

### Permission Validation

**PERM-001: Undeclared Environment Variables**
- **Severity**: HIGH
- **Pattern**: `os.environ` usage not declared in frontmatter
- **Fix**: Add to `metadata.openclaw.requires.env`

**PERM-002: Undeclared Binary Dependencies**
- **Severity**: MEDIUM
- **Pattern**: External binary usage not declared
- **Fix**: Add to `metadata.openclaw.requires.bins`

**PERM-003: Unused Declarations**
- **Severity**: LOW
- **Pattern**: Declared permissions never used
- **Fix**: Remove from frontmatter or verify implementation

### File Operations

**FILE-001: Path Traversal**
- **Severity**: CRITICAL
- **Pattern**: User input in file paths without validation
- **Fix**: Use `Path.resolve()` and validate against base directory
- **CWE**: CWE-22

**FILE-002: Unsafe Permissions**
- **Severity**: MEDIUM
- **Pattern**: `chmod(0o777)`, `chmod(0o666)`
- **Fix**: Use minimum required permissions (`0o600` for files, `0o700` for directories)
- **CWE**: CWE-732

### Command Execution

**CMD-001: Shell Injection**
- **Severity**: CRITICAL/HIGH
- **Pattern**: `shell=True`, `os.system()`, `eval()`, `exec()`
- **Fix**: Use list arguments in subprocess, never use shell=True
- **CWE**: CWE-78

**CMD-002: Missing Command Timeout**
- **Severity**: MEDIUM
- **Pattern**: `subprocess` calls without timeout
- **Fix**: Add `timeout=30` parameter

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No issues found |
| 1 | High severity issues found |
| 2 | Critical issues found |

## Examples

### Audit Before Publishing

```bash
# Check your skill before packaging
scripts/audit.py ~/.claude/skills --skill my-new-skill

# If any issues found, fix them and re-run
scripts/audit.py ~/.claude/skills --skill my-new-skill --min-risk HIGH
```

### CI/CD Integration

```bash
# In GitHub Actions or similar
- name: Security Audit
  run: |
    python scripts/audit.py ./skills --format json --output audit-report.json

- name: Check Results
  run: |
    if [ $? -eq 2 ]; then
      echo "Critical issues found!"
      exit 1
    fi
```

### Review Third-Party Skills

```bash
# Before installing a community skill
git clone https://github.com/user/skill-repo /tmp/skill-review
scripts/audit.py /tmp/skill-review --format markdown --output review.md
cat review.md
```

## Best Practices

1. **Run Regularly**: Audit skills monthly or after updates
2. **Prioritize**: Fix CRITICAL issues immediately, HIGH within 30 days
3. **Verify**: Re-scan after fixes to validate improvements
4. **Track**: Monitor security scores over time
5. **Educate**: Use findings to learn secure coding patterns

## Security Score Calculation

Each skill receives a security score from 0-100:

- Starts at 100
- Deduct points based on findings:
  - CRITICAL: -10 points
  - HIGH: -5 points
  - MEDIUM: -2 points
  - LOW: -1 point

Overall score is the average across all audited skills.

## Troubleshooting

**No skills found**
- Verify the skills directory path
- Ensure each skill has a SKILL.md file

**Import errors**
- Make sure you're running from the skill root directory
- Check that all scanner files exist in `scripts/scanners/`

**Permission errors**
- Ensure the script has execute permissions: `chmod +x scripts/audit.py`
