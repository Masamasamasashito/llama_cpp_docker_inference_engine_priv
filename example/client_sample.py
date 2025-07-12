import requests

API_URL = "http://localhost:8081/completion"

payload = {
    "prompt": "今日の天気は",
    "n_predict": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "logprobs": True,
    "top_logprobs": 3
}

response = requests.post(API_URL, json=payload)
response.raise_for_status()

print("=== Llama.cpp API 応答 ===")
print(response.json())
