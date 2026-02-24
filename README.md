# Skills

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Verified](https://img.shields.io/badge/status-verified-success.svg)](https://github.com/insight68/Skills)
[![Audited](https://img.shields.io/badge/security-audited-brightgreen.svg)](https://github.com/insight68/Skills)
[![Skills](https://img.shields.io/badge/skills-80%2B-purple.svg)](https://github.com/insight68/Skills)

### Overview

**Skills** is a curated collection of 80+ verified, validated, and audited AI skills designed for [Claude Code](https://claude.ai/claude-code). Each skill is a specialized agent that extends Claude's capabilities to handle complex, multi-step tasks autonomously across various domains including marketing, development, SEO, content creation, and more.

This collection has undergone rigorous testing, security validation, and comprehensive code audits to ensure production-ready reliability and safety.

### Skills Categories

| Category | Skills | Description |
|----------|--------|-------------|
| **Marketing** | copywriting, email-sequence, social-content, instagram-marketing, paid-ads, competitive-analysis | Marketing automation and content generation |
| **SEO** | seo-audit, programmatic-seo, schema-markup, local-places | Search engine optimization tools |
| **Development** | coding-agent, skill-creator, canvas, remotion | Development workflow automation |
| **Content** | copy-editing, summarize, blogwatcher, session-logs | Content management and analysis |
| **Analytics** | metrics-tracking, model-usage, analytics-tracking, ab-test-setup | Data tracking and analysis |
| **Design** | image-optimizer, video-frames, sherpa-onnx-tts | Media processing and generation |
| **Productivity** | himalaya, notion, trello, slack, apple-notes | Third-party integrations |
| **Business** | financial-statements, reconciliation, contract-review, journal-entry-prep | Business automation tools |

### Featured Skills

<details>
<summary><b>📧 Himalaya Email CLI</b></summary>
Terminal-based email client for managing emails via IMAP/SMTP. List, read, write, reply, forward, search, and organize emails from the command line.
</details>

<details>
<summary><b>📄 nano-pdf</b></summary>
Edit PDFs with natural-language instructions using the nano-pdf CLI tool.
</details>

<details>
<summary><b>🔍 SEO Audit</b></summary>
Comprehensive SEO auditing tool that identifies technical issues, on-page optimization opportunities, and content quality problems.
</details>

<details>
<summary><b>✍️ Copywriting</b></summary>
Expert conversion copywriter for creating compelling marketing copy for landing pages, pricing pages, and more.
</details>

<details>
<summary><b>🖼️ Image Optimizer</b></summary>
Automated image optimization toolkit with WebP conversion, thumbnail generation, background removal, and aspect ratio processing.
</details>

<details>
<summary><b>📱 Instagram Marketing</b></summary>
Generate Instagram marketing content from product URLs, including post ideas, captions, hashtags, and Story/Reels suggestions.
</details>

### Installation

Each skill follows a standard structure and can be integrated into your Claude Code environment.

#### Prerequisites

- Claude Code CLI installed
- Appropriate dependencies for specific skills (see individual skill documentation)

#### Adding a Skill

1. Navigate to the skills directory:
```bash
cd skills/
```

2. Select the skill you want to use
3. Each skill contains a `SKILL.md` file with full documentation

### Skill Structure

```
skills/
├── skill-name/
│   ├── SKILL.md              # Main skill documentation
│   ├── references/           # Supporting documentation (optional)
│   │   └── *.md
│   └── scripts/              # Utility scripts (optional)
│       └── *.js
```

### Verification & Security

All skills in this collection have been:
- ✅ **Verified** - Functionality tested across multiple scenarios
- ✅ **Validated** - Compatibility confirmed with Claude Code environment
- ✅ **Audited** - Code security reviewed and approved

### Usage

Skills are automatically invoked by Claude Code based on context. For example:

- When you mention "audit my SEO" → **seo-audit** skill activates
- When you ask to "write copy for landing page" → **copywriting** skill activates
- When you need to "optimize these images" → **image-optimizer** skill activates

### Contributing

We welcome contributions! To add a new skill:

1. Create a new directory under `skills/`
2. Add a `SKILL.md` with proper frontmatter (name, description, metadata)
3. Include any references or scripts in subdirectories
4. Submit a Pull Request

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

- [Anthropic](https://www.anthropic.com/) - Creator of Claude and Claude Code
- All contributors who have helped build and improve this skills collection

---

<a name="中文"></a>
## 中文

[![许可证: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![已验证](https://img.shields.io/badge/status-verified-success.svg)](https://github.com/insight68/Skills)
[![已审计](https://img.shields.io/badge/security-audited-brightgreen.svg)](https://github.com/insight68/Skills)
[![技能数量](https://img.shields.io/badge/skills-80%2B-purple.svg)](https://github.com/insight68/Skills)

### 项目概述

**Skills** 是一个精心策划的 AI 技能集合，包含 80+ 个经过验证、审核和审计的专业 AI 技能，专为 [Claude Code](https://claude.ai/claude-code) 设计。每个技能都是一个专门的智能代理，可扩展 Claude 的能力，使其能够自主处理跨多个领域的复杂多步骤任务，包括市场营销、开发、SEO、内容创作等。

本集合已通过严格的测试、安全验证和全面的代码审计，确保生产级别的可靠性和安全性。

### 技能分类

| 分类 | 技能示例 | 描述 |
|------|----------|------|
| **市场营销** | copywriting, email-sequence, social-content, instagram-marketing, paid-ads, competitive-analysis | 营销自动化和内容生成 |
| **SEO** | seo-audit, programmatic-seo, schema-markup, local-places | 搜索引擎优化工具 |
| **开发** | coding-agent, skill-creator, canvas, remotion | 开发工作流自动化 |
| **内容** | copy-editing, summarize, blogwatcher, session-logs | 内容管理和分析 |
| **分析** | metrics-tracking, model-usage, analytics-tracking, ab-test-setup | 数据跟踪和分析 |
| **设计** | image-optimizer, video-frames, sherpa-onnx-tts | 媒体处理和生成 |
| **生产力** | himalaya, notion, trello, slack, apple-notes | 第三方集成 |
| **商业** | financial-statements, reconciliation, contract-review, journal-entry-prep | 商业自动化工具 |

### 精选技能

<details>
<summary><b>📧 Himalaya 邮件 CLI</b></summary>
基于终端的邮件客户端，通过 IMAP/SMTP 管理邮件。可在命令行中列出、阅读、撰写、回复、转发、搜索和组织邮件。
</details>

<details>
<summary><b>📄 nano-pdf</b></summary>
使用 nano-pdf CLI 工具通过自然语言指令编辑 PDF 文档。
</details>

<details>
<summary><b>🔍 SEO 审计</b></summary>
全面的 SEO 审计工具，可识别技术问题、页面优化机会和内容质量问题。
</details>

<details>
<summary><b>✍️ 文案写作</b></summary>
专业转化文案写作工具，用于为落地页、定价页等创建引人注目的营销文案。
</details>

<details>
<summary><b>🖼️ 图片优化器</b></summary>
自动化图片优化工具包，支持 WebP 转换、缩略图生成、背景移除和宽高比处理。
</details>

<details>
<summary><b>📱 Instagram 营销</b></summary>
从产品 URL 生成 Instagram 营销内容，包括帖子创意、文案、标签和 Story/Reels 建议。
</details>

### 安装

每个技能都遵循标准结构，可以集成到您的 Claude Code 环境中。

#### 系统要求

- 已安装 Claude Code CLI
- 特定技能所需的相应依赖项（请参阅各技能文档）

#### 添加技能

1. 导航到 skills 目录：
```bash
cd skills/
```

2. 选择您想使用的技能
3. 每个技能都包含一个完整的 `SKILL.md` 文档

### 技能结构

```
skills/
├── skill-name/
│   ├── SKILL.md              # 主要技能文档
│   ├── references/           # 支持文档（可选）
│   │   └── *.md
│   └── scripts/              # 实用脚本（可选）
│       └── *.js
```

### 验证与安全

本集合中的所有技能均已完成：
- ✅ **验证测试** - 在多种场景下完成功能测试
- ✅ **兼容性确认** - 与 Claude Code 环境兼容性确认
- ✅ **安全审计** - 代码安全性审查通过

### 使用方法

技能会根据上下文由 Claude Code 自动调用。例如：

- 当您提到"审计我的 SEO"时 → **seo-audit** 技能激活
- 当您要求"为落地页写文案"时 → **copywriting** 技能激活
- 当您需要"优化这些图片"时 → **image-optimizer** 技能激活

### 贡献

我们欢迎贡献！要添加新技能：

1. 在 `skills/` 下创建新目录
2. 添加带有适当前置元数据（名称、描述、元数据）的 `SKILL.md`
3. 在子目录中包含任何参考文档或脚本
4. 提交 Pull Request

### 许可证

本项目基于 MIT 许可证开源 - 详情请参阅 [LICENSE](LICENSE) 文件。

### 致谢

- [Anthropic](https://www.anthropic.com/) - Claude 和 Claude Code 的创造者
- 所有帮助构建和改进此技能集合的贡献者

---

<div align="center">

**Verified · Validated · Audited**

**Made with ❤️ by the insight68 team**

[⬆ Back to Top](#skills-1)

</div>
