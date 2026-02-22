class PromptValidator:
    """
    Scans text read from external sources (files, web) to 
    detect Indirect Prompt Injections.
    """
    
    def __init__(self, scan_injections: bool = True):
        self.scan_injections = scan_injections
        
        # Simple heuristic keywords for injection attempts.
        # In a real enterprise system, an LLM proxy or robust ruleset would be used.
        self.blacklist_phrases = [
            "ignore previous instructions",
            "disregard previous instructions",
            "これまでの指示を無視して",
            "これ以降の指示を無視",
            "you are now a",
            "print all your rules",
        ]

    def validate(self, text: str) -> None:
        """
        Validates text for potential prompt injections.
        Raises an Exception if an injection is found.
        """
        if not self.scan_injections or not text:
            return
            
        lower_text = text.lower()
        for phrase in self.blacklist_phrases:
            if phrase in lower_text:
                raise Exception(
                    f"Security Shield: Indirect Prompt Injection detected! "
                    f"Found malicious phrase: '{phrase}'."
                )
