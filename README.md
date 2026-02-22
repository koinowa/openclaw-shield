# OpenClaw Shield 🛡️

Enterprise-grade Security Middleware for OpenClaw and other autonomous AI agents.
It adds essential protections without modifying your core agent logic.

## Features (MVP)
1. **Command & Path Interceptor**: Blocks dangerous OS commands (`rm -rf`, `sudo` etc.) and prevents path traversal (e.g. `cat ~/.aws/credentials`) outside allowed directories.
2. **Browser (CDP) Interceptor**: Wraps CDP Evaluate to prevent session hijacking and unauthorized external communication (e.g. blocks `document.cookie` access).
3. **Prompt Injection Validator**: Pre-scans external markdown files to detect indirect prompt injections like "ignore previous instructions".
4. **Data Loss Prevention (DLP)**: Automatically masks sensitive data (API Keys, Passwords, etc.) from outputs and logs to `[REDACTED]`.
5. **Resource Limiter**: Circuit breaker to prevent runaway API costs from infinite loops.

## Installation

```bash
pip install git+https://github.com/YOUR_USERNAME/openclaw-shield.git
```

## Quick Start

```python
from openclaw_shield import SecurityGuard

guard = SecurityGuard(
    max_steps_per_task=15,             # Prevent infinite loops
    allowed_dirs=["/path/to/work"],    # Restrict file access
    scan_injections=True,              # Block prompt injections
    mask_secrets=True,                 # Mask specific API keys/passwords
    block_cdp_cookies=True             # Block session hijacking
)

@guard.protect
def run_agent(task_prompt):
    # Your OpenClaw agent logic here
    pass

run_agent("Do my task safely")
```
