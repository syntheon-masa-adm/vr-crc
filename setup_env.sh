#!/usr/bin/env bash
# ============================================================
# VR-CRC Phase 1: Environment Setup Script
# Ollama Model Storage → External SSD Isolation
# ============================================================

set -euo pipefail

SSD_BASE="/Volumes/髙橋柾喜の医学格納庫の予備"
OLLAMA_MODELS_DIR="${SSD_BASE}/ollama_models"
WORKSPACE="${SSD_BASE}/vr-crc-workspace"

echo "🚀 VR-CRC Phase 1: Environment Setup Initiated"
echo "================================================"
echo "📍 SSD Path: ${SSD_BASE}"
echo "🧠 Ollama Models Dir: ${OLLAMA_MODELS_DIR}"
echo "📁 Workspace: ${WORKSPACE}"
echo ""

# --- 1. Create Ollama model storage on SSD ---
if [ ! -d "${OLLAMA_MODELS_DIR}" ]; then
    mkdir -p "${OLLAMA_MODELS_DIR}"
    echo "✅ Created Ollama model directory on SSD"
else
    echo "ℹ️  Ollama model directory already exists"
fi

# --- 2. Export OLLAMA_MODELS env variable ---
export OLLAMA_MODELS="${OLLAMA_MODELS_DIR}"
echo "✅ OLLAMA_MODELS set to: ${OLLAMA_MODELS}"

# --- 3. Add to shell profile if not already present ---
SHELL_PROFILE="${HOME}/.zshrc"
EXPORT_LINE="export OLLAMA_MODELS=\"${OLLAMA_MODELS_DIR}\""

if ! grep -qF "${OLLAMA_MODELS_DIR}" "${SHELL_PROFILE}" 2>/dev/null; then
    echo "" >> "${SHELL_PROFILE}"
    echo "# VR-CRC: Ollama models stored on external SSD" >> "${SHELL_PROFILE}"
    echo "${EXPORT_LINE}" >> "${SHELL_PROFILE}"
    echo "✅ Added OLLAMA_MODELS to ${SHELL_PROFILE}"
else
    echo "ℹ️  OLLAMA_MODELS already configured in ${SHELL_PROFILE}"
fi

# --- 4. Verify Ollama is running / start if needed ---
if ! pgrep -x "ollama" > /dev/null 2>&1; then
    echo "⚡ Starting Ollama server..."
    OLLAMA_MODELS="${OLLAMA_MODELS_DIR}" ollama serve &
    sleep 3
    echo "✅ Ollama server started"
else
    echo "ℹ️  Ollama server already running"
fi

# --- 5. Pull deepseek-r1:8b to external SSD ---
echo ""
echo "📥 Pulling deepseek-r1:8b model to external SSD..."
echo "   (This may take 10-20 minutes depending on connection speed)"
echo ""
OLLAMA_MODELS="${OLLAMA_MODELS_DIR}" ollama pull deepseek-r1:8b

echo ""
echo "✅ deepseek-r1:8b successfully installed on external SSD"

# --- 6. Sanity Check: API connectivity test ---
echo ""
echo "🔬 Running API Sanity Check..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    http://localhost:11434/api/tags 2>/dev/null || echo "000")

if [ "${RESPONSE}" = "200" ]; then
    echo "✅ Ollama API: ONLINE (http://localhost:11434)"
    echo ""
    echo "📋 Available Models:"
    OLLAMA_MODELS="${OLLAMA_MODELS_DIR}" ollama list
else
    echo "⚠️  Ollama API not responding (HTTP ${RESPONSE})"
    echo "   Please run: ollama serve"
fi

echo ""
echo "================================================"
echo "🎯 VR-CRC Phase 1: COMPLETE"
echo "   Workspace: ${WORKSPACE}"
echo "   Model Storage: ${OLLAMA_MODELS_DIR}"
echo "   Next: Run python3 ${WORKSPACE}/src/sanity_check.py"
echo "================================================"
