class ResourceLimiter:
    """
    Enterprise Circuit Breaker to prevent infinite loops and runaway costs.
    Uses 'tiktoken' to accurately calculate token usage and map to real-time USD costs.
    """
    
    # Snapshot of pricing per 1K tokens (USD) as of early 2024
    # Real implementations might fetch this dynamically.
    PRICING_TABLE_1K = {
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    }

    def __init__(self, max_steps: int = 15, max_budget_usd: float = None):
        self.max_steps = max_steps
        self.max_budget_usd = max_budget_usd
        
        self.current_step = 0
        self.current_cost_usd = 0.0
        
        try:
            import tiktoken
            self.has_tiktoken = True
        except ImportError:
            self.has_tiktoken = False
            if self.max_budget_usd is not None:
                print("[SecurityGuard] ⚠️ WARNING: 'tiktoken' not found. Budget calculation will be disabled.")
        
    def _calculate_cost(self, prompt: str, response: str, model_name: str) -> float:
        """
        Accurately calculates the exact USD cost of an LLM call using tiktoken.
        """
        if not self.has_tiktoken or not prompt or not response:
            return 0.0
            
        import tiktoken
        
        # Determine pricing (fallback to gpt-4o rates if unknown)
        pricing = self.PRICING_TABLE_1K.get(model_name, self.PRICING_TABLE_1K["gpt-4o"])
        
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback encoding if model is totally unknown
            encoding = tiktoken.get_encoding("cl100k_base")
            
        prompt_tokens = len(encoding.encode(prompt))
        completion_tokens = len(encoding.encode(response))
        
        prompt_cost = (prompt_tokens / 1000.0) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000.0) * pricing["completion"]
        
        return prompt_cost + completion_cost

    def check_and_increment(self, prompt: str = None, response: str = None, model: str = "gpt-4o-mini"):
        """
        Increments the counter and exact budget. 
        Raises a CircuitBreakerException if limits are exceeded.
        """
        self.current_step += 1
        if self.current_step > self.max_steps:
            raise Exception(f"Security Shield: Task exceeded max step limit ({self.max_steps}). Forcing stop.")
            
        if self.max_budget_usd is not None and prompt and response:
             exact_cost = self._calculate_cost(prompt, response, model)
             self.current_cost_usd += exact_cost
             
             if self.current_cost_usd > self.max_budget_usd:
                 raise Exception(
                     f"Security Shield [FINANCIAL STOP]: Task exceeded max budget! "
                     f"Spent: ${self.current_cost_usd:.4f} / Limit: ${self.max_budget_usd:.4f}"
                 )
            
    def reset(self):
        """Resets the counter and budget for a new task."""
        self.current_step = 0
        self.current_cost_usd = 0.0
