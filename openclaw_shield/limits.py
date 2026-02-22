class ResourceLimiter:
    """
    Circuit Breaker pattern to prevent infinite loops and runaway costs.
    """
    def __init__(self, max_steps: int = 15, max_budget_usd: float = None):
        self.max_steps = max_steps
        self.max_budget_usd = max_budget_usd
        
        self.current_step = 0
        self.current_cost_usd = 0.0
        
    def check_and_increment(self, step_cost_usd: float = 0.0):
        """
        Increments the counter/budget and raises a CircuitBreakerException if limits are exceeded.
        """
        self.current_step += 1
        if self.current_step > self.max_steps:
            raise Exception(f"Security Shield: Task exceeded max step limit ({self.max_steps}). Forcing stop.")
            
        self.current_cost_usd += step_cost_usd
        if self.max_budget_usd is not None and self.current_cost_usd > self.max_budget_usd:
            raise Exception(
                f"Security Shield [FINANCIAL STOP]: Task exceeded max budget! "
                f"Spent: ${self.current_cost_usd:.4f} / Limit: ${self.max_budget_usd:.4f}"
            )
            
    def reset(self):
        """Resets the counter and budget for a new task."""
        self.current_step = 0
        self.current_cost_usd = 0.0
