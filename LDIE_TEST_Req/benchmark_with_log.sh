#!/bin/bash
# LDIE ベンチマーク（条件自動記録付き）
# Usage: bash LDIE_TEST_Req/benchmark_with_log.sh [COMPOSE_FILE] [PORT]
# Example: bash LDIE_TEST_Req/benchmark_with_log.sh docker-compose.yml 8081
#
# 結果は LDIE_TEST_Req/benchmark_log.csv に追記される

COMPOSE_FILE=${1:-docker-compose.yml}
PORT=${2:-8081}
LOGFILE="LDIE_TEST_Req/benchmark_log.csv"
ENV_FILE="LDIE_Infra_Docker/.env"

# ヘッダー作成（ファイルが無い場合）
if [ ! -f "$LOGFILE" ]; then
  echo "timestamp,compose_file,port,model,ctx_size,parallel,threads,gpu_layers,ollama,gpu_fan,gpu_temp,gpu_vram_used_mib,tok_per_sec" > "$LOGFILE"
fi

# .env から値を取得
MODEL=$(grep '^LLAMA_MODEL_FILE=' "$ENV_FILE" | cut -d= -f2)
CTX=$(grep '^LLAMA_CTX_SIZE=' "$ENV_FILE" | cut -d= -f2)
PARALLEL=$(grep '^LLAMA_N_PARALLEL=' "$ENV_FILE" | cut -d= -f2)
GPU_LAYERS=$(grep '^LLAMA_N_GPU_LAYERS=' "$ENV_FILE" | cut -d= -f2)

# docker-compose からデフォルト threads を取得（.env に無い場合）
THREADS=$(grep '^LLAMA_THREADS=' "$ENV_FILE" | cut -d= -f2)
if [ -z "$THREADS" ]; then
  THREADS=$(grep -o 'LLAMA_THREADS:-[0-9]*' "LDIE_Infra_Docker/$COMPOSE_FILE" | head -1 | sed 's/LLAMA_THREADS:-//')
fi

# Ollama 確認
OLLAMA=$(nvidia-smi | grep -ci ollama)
if [ "$OLLAMA" -gt 0 ]; then OLLAMA_STATUS="running"; else OLLAMA_STATUS="stopped"; fi

# GPU状態
GPU_FAN=$(nvidia-smi --query-gpu=fan.speed --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
GPU_VRAM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')

# 計測
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
RESULT=$(curl -s -X POST "http://localhost:${PORT}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":50}" \
  | grep -o '"predicted_per_second":[0-9.]*' | head -1 | cut -d: -f2)

# 結果表示
echo "=== Benchmark Result ==="
echo "Time:       $TIMESTAMP"
echo "Compose:    $COMPOSE_FILE"
echo "Port:       $PORT"
echo "Model:      $MODEL"
echo "ctx_size:   $CTX"
echo "parallel:   $PARALLEL"
echo "threads:    $THREADS"
echo "gpu_layers: $GPU_LAYERS"
echo "Ollama:     $OLLAMA_STATUS"
echo "GPU Fan:    ${GPU_FAN}%"
echo "GPU Temp:   ${GPU_TEMP}°C"
echo "GPU VRAM:   ${GPU_VRAM} MiB"
echo "tok/s:      $RESULT"
echo "========================"

# CSV追記
echo "\"$TIMESTAMP\",\"$COMPOSE_FILE\",$PORT,\"$MODEL\",$CTX,$PARALLEL,$THREADS,$GPU_LAYERS,$OLLAMA_STATUS,${GPU_FAN},${GPU_TEMP},${GPU_VRAM},$RESULT" >> "$LOGFILE"
echo "Logged to $LOGFILE"
