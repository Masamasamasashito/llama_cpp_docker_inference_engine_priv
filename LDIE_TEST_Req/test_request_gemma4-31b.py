import requests

API_URL = "http://localhost:8081/v1/chat/completions"

payload = {
    "model": "gemma-4-31B-it-Q4_K_M",
    "messages": [
        {"role": "user", "content": "今日の天気は"}
    ],
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "logprobs": True,
    "top_logprobs": 3
}

response = requests.post(API_URL, json=payload)
response.raise_for_status()

print("=== Gemma 4 31B IT API 応答 ===")
data = response.json()
print(data["choices"][0]["message"]["content"])
