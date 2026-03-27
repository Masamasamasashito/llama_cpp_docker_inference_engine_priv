import requests

API_URL = "http://localhost:8081/v1/chat/completions"

payload = {
    "model": "DeepSeek-R1-Distill-Qwen-32B-Q4_K_M",
    "messages": [
        {"role": "user", "content": "なぜ空は青いのか、ステップバイステップで論理的に説明してください"}
    ],
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9,
    "logprobs": True,
    "top_logprobs": 3
}

response = requests.post(API_URL, json=payload)
response.raise_for_status()

print("=== DeepSeek R1 32B API 応答 ===")
data = response.json()
print(data["choices"][0]["message"]["content"])
