class ResourceLimiter:
    """
    Ultimate Circuit Breaker. 
    Prevents Infinite Loops, CJK Token Drain, and Output Inflation.
    """
    
    PRICING_TABLE_1K = {
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    }

    def __init__(
        self, 
        max_steps: int = 15, 
        max_budget_usd: float = None, 
        max_chars_per_request: int = 50000,
        fallback_cost_cjk_multiplier_usd: float = 0.008
    ):
        self.max_steps = max_steps
        self.max_budget_usd = max_budget_usd
        self.max_chars_per_request = max_chars_per_request
        # CJK characters consume vastly more tokens. This multiplier ensures safety for unknown models.
        self.fallback_cost_cjk_multiplier_usd = fallback_cost_cjk_multiplier_usd
        
        self.current_step = 0
        self.current_cost_usd = 0.0
        
    def _calculate_cost(self, prompt: str, response: str, model_name: str) -> float:
        base_model = model_name
        for prefix in self.PRICING_TABLE_1K.keys():
            if model_name.startswith(prefix):
                base_model = prefix
                break
                
        if base_model in self.PRICING_TABLE_1K:
            try:
                import tiktoken
                pricing = self.PRICING_TABLE_1K[base_model]
                try:
                    encoding = tiktoken.encoding_for_model(base_model)
                except KeyError:
                    encoding = tiktoken.get_encoding("cl100k_base")
                    
                p_cost = (len(encoding.encode(prompt)) / 1000.0) * pricing["prompt"]
                c_cost = (len(encoding.encode(response)) / 1000.0) * pricing["completion"]
                return p_cost + c_cost
            except ImportError:
                pass
                
        # Ultimate Fallback: High CJK-safe character ratio calculation
        # If the model is not found in our pre-approved PRICING_TABLE, we MUST use the fallback multiplier.
        total_chars = len(prompt) + len(response)
        estimated_cost = (total_chars / 1000.0) * self.fallback_cost_cjk_multiplier_usd
        return estimated_cost

    def check_and_increment(self, prompt: str = None, response: str = None, model: str = "gpt-4o-mini"):
        self.current_step += 1
        if self.current_step > self.max_steps:
            raise Exception(f"Security Shield: Task exceeded max step limit ({self.max_steps}). Forcing stop.")
            
        # Defense against Output Inflation / Context Saturation
        if prompt and response:
            if self.max_budget_usd is not None:
                 exact_cost = self._calculate_cost(prompt, response, model)
                 self.current_cost_usd += exact_cost
                 
                 if self.current_cost_usd > self.max_budget_usd:
                     raise Exception(
                         f"Security Shield [FINANCIAL STOP]: Task exceeded max budget! "
                         f"Spent: ${self.current_cost_usd:.4f} / Limit: ${self.max_budget_usd:.4f}"
                     )

            if len(prompt) + len(response) > self.max_chars_per_request:
                raise Exception(
                    f"Security Shield [HARD LIMIT]: Text volume exceeds {self.max_chars_per_request} chars. "
                    "Blocked to prevent Output Inflation / API Wallet Drain."
                )
            
    def reset(self):
        self.current_step = 0
        self.current_cost_usd = 0.0
