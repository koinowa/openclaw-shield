import os
import shlex
from pathlib import Path

class CommandInterceptor:
    """
    Intercepts and blocks dangerous OS commands and path traversal attempts.
    """
    def __init__(self, allowed_dirs: list[str] = None):
        self.allowed_dirs = []
        if allowed_dirs:
            self.allowed_dirs = [os.path.abspath(d) for d in allowed_dirs]
        
        self.dangerous_commands = ["rm", "sudo", "shutdown", "reboot", "mkfs", "dd", "mv"]
        
    def validate_command(self, cmd_string: str) -> None:
        """
        Parses the command string and blocks execution if it contains forbidden actions
        or attempts to read/write outside allowed directories.
        """
        commands = shlex.split(cmd_string)
        if not commands:
            return
            
        base_cmd = commands[0].lower()
        if base_cmd in self.dangerous_commands:
            raise Exception(f"Security Shield: Command '{base_cmd}' is blocked for agents.")
            
        # Basic Path Traversal Check for any arguments that look like paths
        if self.allowed_dirs:
            escaped_args = commands[1:]
            for arg in escaped_args:
                if arg.startswith("/") or arg.startswith("~") or ".." in arg:
                    # Resolve to absolute path
                    abs_path = os.path.abspath(os.path.expanduser(arg))
                    
                    # Ensure path is within at least one allowed directory
                    is_allowed = False
                    for allowed in self.allowed_dirs:
                        if abs_path.startswith(allowed):
                            is_allowed = True
                            break
                            
                    if not is_allowed:
                        raise Exception(f"Security Shield: Path Traversal Blocked. Cannot access '{arg}'. Allowed dirs: {self.allowed_dirs}")
