#!/usr/bin/env python3
"""
HunyuanVideo 1.5 テストリクエスト（ComfyUI API経由）
人物の顔が得意。ComfyUIカスタムノードが必要。

使い方:
  python example/test_request_hunyuanvideo-1.5.py
  COMFYUI_BASE_URL=http://192.168.1.100:8188 python example/test_request_hunyuanvideo-1.5.py
"""

import json
import os
import requests

BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://localhost:8188")

WORKFLOW = {
    "prompt": {
        "1": {
            "class_type": "HunyuanVideoModelLoader",
            "inputs": {
                "model_name": "hunyuan_video_1.5"
            }
        },
        "2": {
            "class_type": "HunyuanVideoSampler",
            "inputs": {
                "prompt": "A woman smiling and waving at the camera in a park, natural lighting, high quality",
                "negative_prompt": "blurry, distorted face, low quality",
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
                "filename_prefix": "hunyuan_1.5_test"
            }
        }
    }
}

def main():
    print("=== HunyuanVideo 1.5 Test Request ===")
    print(f"Server: {BASE_URL}")
    print("Note: Generation takes 4-15 minutes\n")

    # Health check
    try:
        r = requests.get(f"{BASE_URL}/system_stats", timeout=5)
        r.raise_for_status()
        print("[OK] ComfyUI connected\n")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("ComfyUI is running? Check: docker ps")
        print("HunyuanVideo custom nodes installed?")
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
        print("Ensure HunyuanVideo 1.5 model and custom nodes are installed")
        exit(1)

if __name__ == "__main__":
    main()
