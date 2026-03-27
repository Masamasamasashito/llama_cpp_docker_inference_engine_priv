import requests

API_URL = "http://localhost:8081/v1/chat/completions"

payload = {
    "model": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M",
    "messages": [
        {"role": "user", "content": "Pythonでフィボナッチ数列を生成する関数を書いてください"}
    ],
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9,
    "logprobs": True,
    "top_logprobs": 3
}

response = requests.post(API_URL, json=payload)
response.raise_for_status()

print("=== Qwen3-Coder-30B API 応答 ===")
data = response.json()
print(data["choices"][0]["message"]["content"])
