import functools

from .filters import DLPFilter
from .limits import ResourceLimiter
from .validators import PromptValidator
from .interceptors import CommandInterceptor, BrowserInterceptor

class SecurityGuard:
    """
    Main Security Middleware for OpenClaw Agents.
    v0.2.0: Added Budget limits, Webhooks, and AI scanning.
    """
    def __init__(
        self,
        # v0.1.0 Basic Config
        max_steps_per_task: int = 15,
        allowed_dirs: list[str] = None,
        scan_injections: bool = True,
        mask_secrets: bool = True,
        block_cdp_cookies: bool = True,
        
        # v0.2.0 Enterprise Config
        max_budget_usd: float = None,
        webhook_url: str = None,
        ai_validation_model: str = None,
    ):
        self.limiter = ResourceLimiter(
            max_steps=max_steps_per_task,
            max_budget_usd=max_budget_usd
        )
        self.dlp = DLPFilter(mask_secrets=mask_secrets)
        self.validator = PromptValidator(
            scan_injections=scan_injections, 
            ai_validation_model=ai_validation_model
        )
        self.cmd_interceptor = CommandInterceptor(
            allowed_dirs=allowed_dirs, 
            webhook_url=webhook_url
        )
        self.browser_interceptor = BrowserInterceptor(
            block_cdp_cookies=block_cdp_cookies
        )

    def protect(self, func):
        """
        A decorator to wrap an agent's main execution loop.
        Resets the circuit breaker and applies global protections.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.limiter.reset()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                print(f"[SecurityGuard] Agent Execution Halted: {e}")
                raise
        return wrapper

    def step(self, step_cost_usd: float = 0.0):
        """
        Called on every loop/step of the agent to track resources and budget.
        """
        self.limiter.check_and_increment(step_cost_usd=step_cost_usd)

    def process_output(self, text: str) -> str:
        """Filters sensitive data from agent's output."""
        return self.dlp.process(text)

    def scan_input(self, text: str) -> None:
        """Validates external input for prompt injections."""
        self.validator.validate(text)

    def validate_command(self, cmd_string: str) -> None:
        """Blocks dangerous OS commands and invalid path accesses."""
        self.cmd_interceptor.validate_command(cmd_string)
        
    def validate_browser_script(self, js_script: str) -> None:
        """Blocks dangerous CDP JS execution like cookie reading."""
        self.browser_interceptor.validate_evaluate_script(js_script)
