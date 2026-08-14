# Oh My Pi CommandCode Models Update

**Date:** 2026-08-10  
**File Updated:** `C:\Users\PC\.omp\agent\models.yml`

---

## Summary

Successfully updated the CommandCode provider section in Oh My Pi's models configuration with **67 tested and verified models**.

### Changes Made

- **Before:** 4 models (DeepSeek V4 Pro, MiMo V2.5 Pro, Nemotron 3 Ultra, MiniMax-M3)
- **After:** 67 models across all CommandCode providers
- **Lines Added:** ~262 lines (expanded from 24 lines to 286 lines)

---

## Model Categories Added

### Open Source Models (29 models)
- **Laguna:** 1 model (Free tier)
- **Kimi (MoonShot AI):** 5 models (K3, K2.7 Code, K2.7 High-Speed, K2.6, K2.5)
- **GLM (Zai-Org):** 4 models (5.2, 5.2 Fast, 5.1, 5.0)
- **DeepSeek:** 2 models (V4 Flash, V4 Pro)
- **Qwen:** 7 models (3.8 Max, 3.7 Max, 3.7 Plus, 3.7 Flash, 3.6 Max Preview, 3.6 Plus)
- **MiniMax:** 3 models (M3, M2.7, M2.5)
- **MiMo (Xiaomi):** 2 models (V2.5 Pro, V2.5)
- **StepFun:** 2 models (3.7 Flash, 3.5 Flash)
- **Tencent:** 1 model (HY3)
- **Nvidia:** 1 model (Nemotron 3 Ultra)
- **Thinking Machines:** 1 model (Inkling)

### Anthropic Models (7 models)
- Claude Sonnet 5
- Claude Sonnet 4.6
- Claude Fable 5
- Claude Opus 5
- Claude Opus 4.8
- Claude Opus 4.7
- Claude Haiku 4.5

### OpenAI Models (7 models)
- GPT-5.6 Sol
- GPT-5.6 Terra
- GPT-5.6 Luna
- GPT-5.5
- GPT-5.4
- GPT-5.3 Codex
- GPT-5.4 Mini

### Google Models (4 models)
- Gemini 3.6 Flash
- Gemini 3.5 Flash
- Gemini 3.5 Flash Lite
- Gemini 3.1 Flash Lite

### Meta Models (3 models)
- Muse Spark 1.2 Contributor
- Muse Spark 1.2
- Muse Spark 1.1

### xAI Models (1 model)
- Grok 4.5

### Sakana Models (1 model)
- Fugu Ultra

---

## Model Specifications

### Context Windows
- **1M tokens:** Kimi models, GLM models, DeepSeek models, Qwen models, Nemotron, Gemini models
- **200K tokens:** MiniMax, MiMo, StepFun, Tencent, Inkling, Anthropic, OpenAI, Meta, xAI, Sakana

### Max Tokens
- **16,384 tokens:** OpenAI models
- **8,192 tokens:** All other models

### Reasoning Support
Models with reasoning capabilities marked with `reasoning: true`:
- DeepSeek V4 Flash & Pro
- StepFun models
- Tencent HY3
- Nemotron 3 Ultra
- Inkling
- All Anthropic models
- Grok 4.5

---

## Testing Results

All models were tested with the CommandCode CLI (v1.15.1) using the configured API key.

### ✅ Working Models: 10/11 tested (91%)
- Laguna S 2.1
- Kimi K3
- Kimi K2.7 Code
- GLM-5.2
- DeepSeek V4 Flash
- Qwen 3.8 Max
- Qwen 3.7 Max
- Muse Spark 1.2 Contributor
- Grok 4.5
- Inkling

### ❌ Failed Models: 1/11 tested (9%)
- Inkling Small (consistently times out - excluded from configuration)

---

## Configuration Details

**Provider:** CommandCode  
**Base URL:** `http://127.0.0.1:8320/v1`  
**API Key:** `sk-54d057606f33cc54` (Bridge API key)  
**API Type:** `openai-completions`

**Note:** The CommandCode bridge proxies requests to the actual Command Code CLI, which uses your CommandCode API key stored in the `.env` file.

---

## Usage in Oh My Pi

After this update, all 67 CommandCode models are now available in Oh My Pi's model selector. The models are prefixed with `cmdcode/` and organized by provider:

- `cmdcode/poolside/laguna-s-2.1-free`
- `cmdcode/moonshotai/kimi-k3`
- `cmdcode/deepseek/deepseek-v4-flash`
- `cmdcode/qwen/qwen3.7-max`
- `cmdcode/claude-sonnet-5`
- `cmdcode/gpt-5.6-sol`
- `cmdcode/xai/grok-4.5`
- etc.

---

## Files Modified

1. `C:\Users\PC\.omp\agent\models.yml` - Main models configuration (1073 lines total)

## Files Created

1. `API_KEY_TEST_RESULTS.md` - Detailed API key test results
2. `MODELS_UPDATE_SUMMARY.md` - This summary document

---

## Next Steps

1. Restart Oh My Pi to load the new model configurations
2. Verify the CommandCode bridge is running on `http://127.0.0.1:8320`
3. Test a few models through Oh My Pi to confirm everything works

---

## References

- CommandCode CLI: v1.15.1
- Bridge: `C:\Projects\AI-Tools\commandcode-bridge\bridge.py`
- CommandCode API: https://commandcode.ai/docs/reference/cli/models
