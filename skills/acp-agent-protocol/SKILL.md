---
name: acp-agent-protocol
description: "Agent Control Protocol (ACP) for OpenClaw - Connect to external AI agents like Claude Code, Codex, Pi, etc."
---

# ACP Agent Protocol Skill

## Overview

Agent Control Protocol (ACP) is OpenClaw's system for connecting to external AI agents for coding and specialized tasks. This skill provides guidance on setting up and using ACP with various AI providers.

## Current Status

**⚠️ ACP Runtime Not Configured**
Error: `ACP runtime backend is not configured. Install and enable the acpx runtime plugin.`

## Installation

### 1. Install acpx Runtime Plugin
```bash
# Check if acpx is available
npm list -g | grep acpx

# If not installed, may need to install from OpenClaw plugins
# (Exact installation method depends on OpenClaw version)
```

### 2. Configure ACP Providers
ACP supports various AI providers:
- **Claude Code** (Anthropic)
- **Codex** (OpenAI)
- **Pi** (Inflection)
- **Gemini** (Google)
- Custom agents

### 3. Set Up Agent Credentials
Each provider requires API keys and configuration:
```bash
# Example: Set up Claude Code
openclaw config set acp.providers.claude-code.apiKey "your-anthropic-key"
openclaw config set acp.providers.claude-code.model "claude-3-5-sonnet-20241022"
```

## Usage

### Basic ACP Client
```bash
# Run interactive ACP client
openclaw acp client

# With specific session
openclaw acp client --session "agent:main:claude-code"
```

### Spawn ACP Sessions Programmatically
```javascript
// Example from OpenClaw sessions_spawn
{
  runtime: "acp",
  agentId: "claude-code",
  task: "Write a Python script to process data",
  mode: "session"
}
```

### Common ACP Agent IDs
- `claude-code` - Anthropic's Claude for coding
- `codex` - OpenAI Codex
- `pi` - Inflection Pi
- `gemini` - Google Gemini
- Custom agent IDs configured in acp.providers

## Configuration

### Gateway Configuration
ACP requires gateway configuration:
```json
{
  "acp": {
    "enabled": true,
    "providers": {
      "claude-code": {
        "type": "anthropic",
        "apiKey": "${ANTHROPIC_API_KEY}",
        "model": "claude-3-5-sonnet-20241022"
      }
    }
  }
}
```

### Environment Variables
```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

## Troubleshooting

### Error: "ACP runtime backend is not configured"
**Solution:** Install acpx runtime plugin
```bash
# Check OpenClaw plugin directory
ls ~/.npm-global/lib/node_modules/openclaw/plugins/

# May need to install separately
npm install -g @openclaw/acpx
```

### Error: "agentId is not allowed"
**Solution:** Configure allowed agents in OpenClaw config
```bash
openclaw config set agents.allowlist "claude-code,codex,pi"
```

### Error: No ACP providers configured
**Solution:** Set up at least one ACP provider
```bash
openclaw config set acp.providers.claude-code.apiKey "your-key"
openclaw config restart
```

## Examples

### 1. Simple Code Review
```bash
openclaw acp client --session "code-review" << EOF
Review this Python function for security issues:

def process_user_input(data):
    return eval(data)
EOF
```

### 2. File Processing Task
```bash
# Create a task file
cat > /tmp/task.md << EOF
Process the CSV file at /data/sample.csv:
1. Clean missing values
2. Calculate averages
3. Generate summary report
EOF

# Run with Claude Code
openclaw acp client --session "claude-code" < /tmp/task.md
```

### 3. Persistent Coding Session
```bash
# Start persistent session
openclaw acp client --session "project-dev" --session-label "webapp-project"

# Session persists across multiple interactions
```

## Integration with Other Skills

### With Coding-Agent Skill
ACP can complement the existing coding-agent skill:
- **coding-agent**: Background processes, file exploration
- **ACP**: Direct agent interaction, specialized coding tasks

### With Session Management
ACP sessions appear in `sessions_list()` and can be managed alongside subagent sessions.

## Security Considerations

1. **API Key Management**: Store keys securely, use environment variables
2. **Session Isolation**: ACP sessions run isolated from main workspace
3. **Cost Monitoring**: Track token usage for paid providers
4. **Rate Limiting**: Configure appropriate rate limits for API calls

## References

- OpenClaw ACP Docs: `https://docs.openclaw.ai/cli/acp`
- Anthropic Claude API: `https://docs.anthropic.com`
- OpenAI Codex: `https://platform.openai.com/docs/guides/code`
- OpenClaw GitHub: `https://github.com/openclaw/openclaw`

## Next Steps

1. Install acpx runtime plugin
2. Configure at least one ACP provider (Claude Code recommended)
3. Test with simple `openclaw acp client` command
4. Integrate with existing workflow for coding tasks

**Note:** ACP setup requires external API keys and may involve costs depending on the provider used.