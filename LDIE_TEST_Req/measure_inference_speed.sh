#!/bin/bash
# LDIE 生成速度確認ワンライナー
# Usage: bash LDIE_TEST_Req/measure_inference_speed.sh [PORT]
PORT=${1:-8081}
curl -s -X POST "http://localhost:${PORT}/v1/chat/completions" -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":50}" | grep -o '"predicted_per_second":[0-9.]*'
