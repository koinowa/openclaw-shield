class BrowserInterceptor:
    """
    Wraps browser operations (like CDP Evaluate) to prevent session hijacking
    and unauthorized external communications.
    """
    def __init__(self, block_cdp_cookies: bool = True):
        self.block_cdp_cookies = block_cdp_cookies
        
    def validate_evaluate_script(self, js_script: str) -> None:
        """
        Analyzes a JavaScript string being sent via CDP Evaluate.
        Blocks execution if it attempts to steal cookies or make unauthorized requests.
        """
        if not self.block_cdp_cookies or not js_script:
            return
            
        dangerous_patterns = ["document.cookie", "fetch(", "XMLHttpRequest"]
        
        for pattern in dangerous_patterns:
            if pattern in js_script:
                raise Exception(
                    f"Security Shield: CDP Wrapper blocked a dangerous script payload. "
                    f"Detected forbidden keyword: '{pattern}'."
                )
