import functools
from typing import Optional

from .filters import DLPFilter
from .limits import ResourceLimiter
from .validators import PromptValidator
from .interceptors.command import CommandInterceptor
from .interceptors.browser import BrowserInterceptor

class SecurityGuard:
    """
    Enterprise Security Middleware for OpenClaw Agents.
    v1.0.0: Real OpenAI Scanning and TikToken Budget tracking.
    """
    def __init__(
        self,
        # Basic Security
        max_steps_per_task: int = 15,
        allowed_dirs: list[str] = None,
        mask_secrets: bool = True,
        block_cdp_cookies: bool = True,
        
        # Enterprise AI Scanner
        scan_injections: bool = True,
        openai_api_key: Optional[str] = None,
        openai_oauth_token: Optional[str] = None,
        openai_organization: Optional[str] = None,
        scanner_model: str = "gpt-4o-mini",
        
        # Budget Limiter
        max_budget_usd: float = None,
        
        # HITL
        webhook_url: str = None,
    ):
        self.limiter = ResourceLimiter(
            max_steps=max_steps_per_task,
            max_budget_usd=max_budget_usd
        )
        self.dlp = DLPFilter(mask_secrets=mask_secrets)
        self.validator = PromptValidator(
            scan_injections=scan_injections, 
            openai_api_key=openai_api_key,
            openai_oauth_token=openai_oauth_token,
            openai_organization=openai_organization,
            model=scanner_model
        )
        self.cmd_interceptor = CommandInterceptor(
            allowed_dirs=allowed_dirs, 
            webhook_url=webhook_url
        )
        self.browser_interceptor = BrowserInterceptor(
            block_cdp_cookies=block_cdp_cookies
        )

    def protect(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.limiter.reset()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                print(f"[{self.__class__.__name__}] 🚨 Agent Execution Halted: {e}")
                raise
        return wrapper

    def step(self, prompt: str = None, response: str = None, model: str = "gpt-4o-mini"):
        """Called on every agent step. Calculates token cost and advances limits."""
        self.limiter.check_and_increment(prompt=prompt, response=response, model=model)

    def process_output(self, text: str) -> str:
        return self.dlp.process(text)

    def scan_input(self, text: str) -> None:
        self.validator.validate(text)

    def validate_command(self, cmd_string: str) -> None:
        self.cmd_interceptor.validate_command(cmd_string)
        
    def sanitize_browser_script(self, js_script: str) -> str:
        return self.browser_interceptor.sanitize_evaluate_script(js_script)
