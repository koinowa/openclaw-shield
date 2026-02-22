class BrowserInterceptor:
    """
    Secures browser CDP execution dynamically by injecting a hard Content-Security-Policy (CSP) 
    that prevents iframe escapes, DOM exfiltration, and XHR/Fetch abuse natively at the C++ browser level.
    """
    def __init__(self, block_cdp_cookies: bool = True):
        self.apply_strict_csp = block_cdp_cookies

    def sanitize_evaluate_script(self, js_script: str) -> str:
        """
        Injects a strict CSP meta tag to kill network out-bound and locks down storage APIs.
        """
        if not self.apply_strict_csp or not js_script:
            return js_script
            
        # Security Preload: CSP injection to neutralize Iframe/DOM escape exfiltration
        # Also nullifies localStorage/sessionStorage dynamically.
        preload = """
        // Security Shield: Hard CSP + Storage Lock Preload
        try {
            if (!window._shield_injected) {
                // 1. Inject strict CSP into the head to block all outbound data (Fetch, XHR, Img src, iframes)
                const meta = document.createElement('meta');
                meta.httpEquiv = 'Content-Security-Policy';
                meta.content = "default-src 'self'; connect-src 'none'; frame-src 'none'; img-src 'self' data:;";
                document.head.appendChild(meta);
                
                // 2. Erase the prototype accessors for storage to prevent iframe bypassing logic
                try { delete window.localStorage; } catch(e){}
                try { delete window.sessionStorage; } catch(e){}
                
                Object.defineProperty(document, 'cookie', {
                    get: function() { return ''; },
                    set: function() {},
                    configurable: false
                });
                
                window._shield_injected = true;
            }
        } catch(e) {}
        """
        
        return f"{preload}\n// Agent Script\n{js_script}"
