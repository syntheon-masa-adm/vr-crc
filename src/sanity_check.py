#!/usr/bin/env python3
"""
VR-CRC Phase 1: Ollama API Sanity Check
deepseek-r1:8b との疎通確認スクリプト
"""

import json
import sys
import time
import urllib.request
import urllib.error

OLLAMA_BASE_URL = "http://localhost:11434"
TARGET_MODEL = "deepseek-r1:8b"

def check_api_health() -> bool:
    """Ollama APIのヘルスチェック"""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            print(f"  ✅ API Online | Available models: {models}")
            return TARGET_MODEL in " ".join(models)
    except Exception as e:
        print(f"  ❌ API Error: {e}")
        return False

def run_medical_sanity_prompt() -> bool:
    """医療コンテキストでの最小限推論テスト"""
    test_prompt = (
        "患者：右側大腸癌、cT3N1M0、RAS野生型、MSS。"
        "この患者の最重要な予後因子を一文で述べよ。"
    )

    payload = {
        "model": TARGET_MODEL,
        "prompt": test_prompt,
        "stream": False,
        "options": {"num_predict": 150, "temperature": 0.1}
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        print(f"  ⏳ Sending medical reasoning prompt...")
        start = time.time()
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            elapsed = time.time() - start
            response_text = result.get("response", "")
            print(f"  ✅ Response received in {elapsed:.1f}s")
            print(f"  📋 Model Output (truncated):\n")
            print("  " + "-" * 60)
            print("  " + response_text[:500].replace("\n", "\n  "))
            print("  " + "-" * 60)
            return bool(response_text)
    except Exception as e:
        print(f"  ❌ Inference Error: {e}")
        return False

def main():
    print()
    print("=" * 65)
    print("  VR-CRC Phase 1: API Sanity Check")
    print("  Target: deepseek-r1:8b via Ollama (localhost:11434)")
    print("=" * 65)
    print()

    # Step 1: Health check
    print("📡 Step 1: API Health Check")
    model_found = check_api_health()
    print()

    if not model_found:
        print("⚠️  deepseek-r1:8b not found in model list.")
        print("   Run: OLLAMA_MODELS=/Volumes/髙橋柾喜の医学格納庫の予備/ollama_models ollama pull deepseek-r1:8b")
        print()
        # Still attempt inference in case model name differs slightly
        print("   Attempting inference anyway with available model...")

    # Step 2: Medical inference test
    print("🧬 Step 2: Medical Reasoning Sanity Test")
    success = run_medical_sanity_prompt()
    print()

    # Result
    if success:
        print("=" * 65)
        print("  ✅ SANITY CHECK PASSED")
        print("  System is operational. Proceed to Phase 2-4.")
        print("=" * 65)
        sys.exit(0)
    else:
        print("=" * 65)
        print("  ❌ SANITY CHECK FAILED")
        print("  Check Ollama server status and model availability.")
        print("=" * 65)
        sys.exit(1)

if __name__ == "__main__":
    main()
