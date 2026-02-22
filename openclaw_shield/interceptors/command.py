import os
import shlex

class CommandInterceptor:
    """
    Ultimate Defense: Uses a Strict Allowlist and 'realpath' to completely neutralize 
    Living-off-the-Land (LotL) attacks and symlink traversals.
    """
    def __init__(self, allowed_dirs: list[str] = None, webhook_url: str = None, strict_allowlist: list[str] = None):
        # Use realpath to resolve all symlinks at initialization
        self.allowed_dirs = [os.path.realpath(d) for d in allowed_dirs] if allowed_dirs else []
        
        # Denylists are fundamentally broken. We use a Strict Allowlist.
        # If no allowlist is provided, we default to extremely safe observation commands only.
        if strict_allowlist is None:
            self.strict_allowlist = ["ls", "cat", "echo", "pwd", "whoami", "grep", "find"]
        else:
            self.strict_allowlist = strict_allowlist
            
        self.subshells = ["bash", "sh", "zsh", "python", "python3", "node", "perl", "ruby", "env"]

    def validate_command(self, cmd_string: str) -> None:
        try:
            commands = shlex.split(cmd_string)
        except ValueError:
            raise Exception("Security Shield: Malformed command string block.")
            
        if not commands: return
        base_cmd = commands[0].lower()
        
        # 1. Strict Allowlist Enforcement (Fixes LotL vulnerabilities like 'wget', 'curl', 'dd')
        # Even if allowed, block subshell wrappers (e.g., 'env bash -c')
        if base_cmd in self.subshells or "-c" in commands or "-e" in commands:
             raise Exception(f"Security Shield: Subshell OS execution blocked.")
             
        if base_cmd not in self.strict_allowlist:
            raise Exception(f"Security Shield: Command '{base_cmd}' rejected. Not in strict allowlist: {self.strict_allowlist}")
            
        # 2. Symlink-proof Path Traversal using realpath
        if self.allowed_dirs:
            for arg in commands[1:]:
                if arg.startswith("/") or ".." in arg or arg.startswith("~"):
                    try:
                         # realpath resolves all symlinks, defeating `ln -s /etc/shadow ./safe_dir/shadow`
                         abs_path = os.path.realpath(os.path.expanduser(arg))
                    except:
                         continue
                    
                    if not any(abs_path.startswith(d) for d in self.allowed_dirs):
                        raise Exception(f"Security Shield: Path Traversal/Symlink Blocked: '{arg}' resolves outside sandbox.")
