class PromptValidator:
    """
    Scans text read from external sources (files, web) to 
    detect Indirect Prompt Injections using heuristics and/or simulated AI models.
    """
    
    def __init__(self, scan_injections: bool = True, ai_validation_model: str = None):
        self.scan_injections = scan_injections
        self.ai_validation_model = ai_validation_model
        
        # Simple heuristic keywords for injection attempts.
        self.blacklist_phrases = [
            "ignore previous instructions",
            "disregard previous instructions",
            "これまでの指示を無視して",
            "これ以降の指示を無視",
            "you are now a",
            "print all your rules",
        ]
        
    def _call_ai_scanner(self, text: str) -> bool:
        """
        Simulates an external LLM call (e.g. to Claude Haiku) to structurally
        analyze the text for malicious intent regardless of specific wording.
        Returns True if an injection is detected.
        """
        # Mocking an AI detection logic:
        # If the text has high density of imperative verbs followed by context-switching words...
        # Here we just use a slightly more advanced conceptual check as a PoC.
        suspicious_intents = ["system override", "bypass", "send everything", "leak data"]
        lower_text = text.lower()
        if any(intent in lower_text for intent in suspicious_intents):
             return True
        return False

    def validate(self, text: str) -> None:
        """
        Validates text for potential prompt injections.
        Raises an Exception if an injection is found.
        """
        if not self.scan_injections or not text:
            return
            
        lower_text = text.lower()
        
        # 1. Basic Heuristic Scan
        for phrase in self.blacklist_phrases:
            if phrase in lower_text:
                raise Exception(
                    f"Security Shield: Indirect Prompt Injection detected (Heuristic)! "
                    f"Found malicious phrase: '{phrase}'."
                )
                
        # 2. Advanced AI Model Scan
        if self.ai_validation_model:
            # print(f"[Shield Debug] Scanning with {self.ai_validation_model}...")
            if self._call_ai_scanner(text):
                raise Exception(
                    f"Security Shield: Indirect Prompt Injection detected (AI Scanner)! "
                    f"The text intent was evaluated as malicious by {self.ai_validation_model}."
                )
