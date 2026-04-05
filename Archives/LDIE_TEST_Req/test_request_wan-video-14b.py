#!/usr/bin/env python3
"""
Wan 2.2 (14B) テストリクエスト（ComfyUI API経由）
高品質動画生成。生成に4-15分程度かかります。

使い方:
  python example/test_request_wan-video-14b.py
  COMFYUI_BASE_URL=http://192.168.1.100:8188 python example/test_request_wan-video-14b.py
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
                "model_name": "wan2.2_14b"
            }
        },
        "2": {
            "class_type": "WanVideoSampler",
            "inputs": {
                "prompt": "A golden retriever running through a field of flowers, cinematic lighting",
                "negative_prompt": "blurry, distorted, low quality",
                "steps": 30,
                "cfg": 7.5,
                "width": 720,
                "height": 480,
                "num_frames": 48,
                "seed": 42
            }
        },
        "3": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "filename_prefix": "wan_14b_test"
            }
        }
    }
}

def main():
    print("=== Wan 2.2 (14B) Test Request ===")
    print(f"Server: {BASE_URL}")
    print("Note: Generation takes 4-15 minutes for 14B model\n")

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
        print("Ensure Wan 2.2 model and nodes are installed in ComfyUI")
        exit(1)

if __name__ == "__main__":
    main()
