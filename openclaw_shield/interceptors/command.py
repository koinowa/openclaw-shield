import os
import shlex

class CommandInterceptor:
    """
    Intercepts and blocks dangerous OS commands and path traversal attempts.
    Features Human-in-the-Loop (HITL) Webhook integration for manual approval overrides.
    """
    def __init__(self, allowed_dirs: list[str] = None, webhook_url: str = None):
        self.allowed_dirs = []
        if allowed_dirs:
            self.allowed_dirs = [os.path.abspath(d) for d in allowed_dirs]
        
        self.dangerous_commands = ["rm", "sudo", "shutdown", "reboot", "mkfs", "dd", "mv"]
        self.webhook_url = webhook_url
        
    def _request_human_approval(self, action_description: str) -> bool:
        """
        Mocks a Webhook call (e.g., Slack) requesting human approval.
        In a real scenario, this would POST to the URL and poll or wait for a callback.
        """
        print(f"\n[HITL Webhook] 🔔 Notification sent to {self.webhook_url}")
        print(f"  Action: {action_description}")
        print(f"  Status: Pending Human Approval...")
        # For the sake of this PoC, we will auto-reject to maintain security, 
        # but the infrastructure is in place.
        return False

    def validate_command(self, cmd_string: str) -> None:
        """
        Parses the command string and blocks execution if it contains forbidden actions
        or attempts to read/write outside allowed directories.
        """
        commands = shlex.split(cmd_string)
        if not commands:
            return
            
        base_cmd = commands[0].lower()
        
        # Block dangerous commands
        if base_cmd in self.dangerous_commands:
            if self.webhook_url:
                approved = self._request_human_approval(f"Dangerous command executed: {cmd_string}")
                if approved:
                    return # Human overrode the block
            raise Exception(f"Security Shield: Command '{base_cmd}' is blocked for agents.")
            
        # Basic Path Traversal Check for any arguments that look like paths
        if self.allowed_dirs:
            escaped_args = commands[1:]
            for arg in escaped_args:
                if arg.startswith("/") or arg.startswith("~") or ".." in arg:
                    abs_path = os.path.abspath(os.path.expanduser(arg))
                    
                    is_allowed = False
                    for allowed in self.allowed_dirs:
                        if abs_path.startswith(allowed):
                            is_allowed = True
                            break
                            
                    if not is_allowed:
                        if self.webhook_url:
                             approved = self._request_human_approval(f"Path traversal outside sandbox: {arg}")
                             if approved:
                                 continue
                        raise Exception(f"Security Shield: Path Traversal Blocked. Cannot access '{arg}'. Allowed dirs: {self.allowed_dirs}")
