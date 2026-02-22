class ResourceLimiter:
    """
    Circuit Breaker pattern to prevent infinite loops and runaway costs.
    """
    def __init__(self, max_steps: int = 15):
        self.max_steps = max_steps
        self.current_step = 0
        
    def check_and_increment(self):
        """
        Increments the counter and raises a CircuitBreakerException if limits are exceeded.
        """
        self.current_step += 1
        if self.current_step > self.max_steps:
            raise Exception(f"Security Shield: Task exceeded max step limit ({self.max_steps}). Forcing stop.")
            
    def reset(self):
        """Resets the counter for a new task."""
        self.current_step = 0
