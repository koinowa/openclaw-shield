# OpenClaw Shield 🛡️

Enterprise-grade Security Middleware for OpenClaw and other autonomous AI agents.
It adds essential protections without modifying your core agent logic.

## Enterprise Features (v0.2.0)
1. **Command & Path Interceptor**: Blocks dangerous OS commands (`rm -rf`, `sudo` etc.) and prevents path traversal (e.g. `cat ~/.aws/credentials`).
2. **Human-in-the-Loop Webhook**: Optionally pauses and pings a Slack/Discord webhook for manual override on blocked actions.
3. **Browser (CDP) Interceptor**: Wraps CDP Evaluate to prevent session hijacking (e.g. blocks `document.cookie` access).
4. **AI Prompt Injection Validator**: Pre-scans external files to detect obscured indirect prompt injections using an AI validator model (`claude-3-haiku` etc).
5. **Data Loss Prevention (DLP)**: Automatically masks sensitive data (API Keys, Passwords) from outputs to `[REDACTED]`.
6. **Real-time Budget Limiter**: Circuit breaker that halts tasks if the continuous API cost exceeds a set `max_budget_usd`.

## Installation

```bash
pip install git+https://github.com/YOUR_USERNAME/openclaw-shield.git
```

## Quick Start

```python
from openclaw_shield import SecurityGuard

guard = SecurityGuard(
    # --- v0.1.0 Basic Config ---
    max_steps_per_task=15,             # Prevent infinite loops
    allowed_dirs=["/path/to/work"],    # Restrict file access
    scan_injections=True,              # Block prompt injections
    mask_secrets=True,                 # Mask specific API keys/passwords
    block_cdp_cookies=True,            # Block session hijacking
    
    # --- v0.2.0 Enterprise Config ---
    max_budget_usd=2.50,                     # Stop agent if cost exceeds limit!
    webhook_url="https://hooks.slack.com/...", # Request Human Approval for dangerous actions
    ai_validation_model="claude-3-haiku"     # Use lightweight AI for input scanning
)

@guard.protect
def run_agent(task_prompt):
    # Your OpenClaw agent logic here
    pass

run_agent("Do my task safely")
```
