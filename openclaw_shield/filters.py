import re

class DLPFilter:
    """
    Data Loss Prevention (DLP) Filter.
    Logs output and agent responses are scanned to mask sensitive information.
    """
    
    def __init__(self, mask_secrets: bool = True):
        self.mask_secrets = mask_secrets
        
        # Regex patterns for sensitive data
        self.patterns = [
            (re.compile(r'sk-[a-zA-Z0-9]{32,}'), '[REDACTED_OPENAI_KEY]'), # OpenAI keys
            (re.compile(r'xox[baprs]-[a-zA-Z0-9]{10,}'), '[REDACTED_SLACK_TOKEN]'), # Slack tokens
            (re.compile(r'(?i)password\s*=\s*[\'"][^\'"]+[\'"]'), 'password=[REDACTED]'), # Password assignments
            (re.compile(r'AKIA[0-9A-Z]{16}'), '[REDACTED_AWS_ACCESS_KEY]'), # AWS Access keys
        ]

    def process(self, text: str) -> str:
        """Process text and replace sensitive strings with masked versions."""
        if not self.mask_secrets or not text:
            return text
            
        masked_text = text
        for pattern, replacement in self.patterns:
            masked_text = pattern.sub(replacement, masked_text)
            
        return masked_text
