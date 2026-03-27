#!/usr/bin/env python3
"""
Wan 2.1 (1.3B) テストリクエスト（ComfyUI API経由）
軽量版。8GB GPUでも動作します。

使い方:
  python example/test_request_wan-video-1.3b.py
  COMFYUI_BASE_URL=http://192.168.1.100:8188 python example/test_request_wan-video-1.3b.py
"""

import json
import os
import requests

BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://localhost:8188")

WORKFLOW = {
    "prompt": {
        "1": {
            "class_type": "WanVideoModelLoader",
            "inputs": {
                "model_name": "wan2.1_1.3b"
            }
        },
        "2": {
            "class_type": "WanVideoSampler",
            "inputs": {
                "prompt": "A cat sitting on a windowsill watching rain",
                "negative_prompt": "blurry, distorted, low quality",
                "steps": 25,
                "cfg": 7.0,
                "width": 512,
                "height": 512,
                "num_frames": 24,
                "seed": 42
            }
        },
        "3": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "filename_prefix": "wan_1.3b_test"
            }
        }
    }
}

def main():
    print("=== Wan 2.1 (1.3B) Test Request ===")
    print(f"Server: {BASE_URL}")

    # Health check
    try:
        r = requests.get(f"{BASE_URL}/system_stats", timeout=5)
        r.raise_for_status()
        print("[OK] ComfyUI connected\n")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("ComfyUI is running? Check: docker ps")
        exit(1)

    # Queue prompt
    try:
        r = requests.post(f"{BASE_URL}/prompt", json=WORKFLOW, timeout=10)
        r.raise_for_status()
        data = r.json()
        prompt_id = data.get("prompt_id", "unknown")
        print(f"[QUEUED] prompt_id: {prompt_id}")
        print("Check ComfyUI WebUI for progress: " + BASE_URL)
    except Exception as e:
        print(f"[ERROR] Queue failed: {e}")
        print("Ensure Wan 2.1 model and nodes are installed in ComfyUI")
        exit(1)

if __name__ == "__main__":
    main()
