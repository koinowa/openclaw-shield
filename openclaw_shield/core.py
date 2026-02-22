import functools

from .filters import DLPFilter
from .limits import ResourceLimiter
from .validators import PromptValidator
from .interceptors import CommandInterceptor, BrowserInterceptor

class SecurityGuard:
    """
    Main Security Middleware for OpenClaw Agents.
    Provides easy-to-use decorators and validation pipelines.
    """
    def __init__(
        self,
        max_steps_per_task: int = 15,
        allowed_dirs: list[str] = None,
        scan_injections: bool = True,
        mask_secrets: bool = True,
        block_cdp_cookies: bool = True,
    ):
        self.limiter = ResourceLimiter(max_steps=max_steps_per_task)
        self.dlp = DLPFilter(mask_secrets=mask_secrets)
        self.validator = PromptValidator(scan_injections=scan_injections)
        self.cmd_interceptor = CommandInterceptor(allowed_dirs=allowed_dirs)
        self.browser_interceptor = BrowserInterceptor(block_cdp_cookies=block_cdp_cookies)

    def protect(self, func):
        """
        A decorator to wrap an agent's main execution loop.
        Resets the circuit breaker and applies global protections.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.limiter.reset()
            # Wrap function execution
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # Basic logging for the security shield
                print(f"[SecurityGuard] Agent Execution Halted: {e}")
                raise
        return wrapper

    def step(self):
        """
        Called on every loop/step of the agent to track resources.
        """
        self.limiter.check_and_increment()

    def process_output(self, text: str) -> str:
        """
        Filters sensitive data from agent's output.
        """
        return self.dlp.process(text)

    def scan_input(self, text: str) -> None:
        """
        Validates external input for prompt injections.
        """
        self.validator.validate(text)

    def validate_command(self, cmd_string: str) -> None:
        """
        Blocks dangerous OS commands and invalid path accesses.
        """
        self.cmd_interceptor.validate_command(cmd_string)
        
    def validate_browser_script(self, js_script: str) -> None:
        """
        Blocks dangerous CDP JS execution like cookie reading.
        """
        self.browser_interceptor.validate_evaluate_script(js_script)
