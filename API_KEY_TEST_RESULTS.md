# CommandCode API Key Test Results

**Test Date:** 2026-08-10  
**API Key:** `user_MyLK6yj3P23fqxNd347trZyqVbK6Qk8VQT9f8tSmfwYPFoMuMTiAK5JFAVMkgNQq4viGaMNZkVnhSyyDweJ9jXg`  
**Command Code CLI Version:** 1.15.1

---

## Summary

- **✓ Working:** 10/11 models (91%)
- **✗ Failed:** 1/11 models (9%)

---

## Detailed Results

### ✓ Working Models (10)

| Model Name | Model ID | Status | Notes |
|------------|----------|--------|-------|
| Laguna S 2.1 | `poolside/laguna-s-2.1-free` | ✓ Working | Free tier model |
| Kimi K3 | `moonshotai/kimi-k3` | ✓ Working | 1M context |
| Kimi K2.7 Code | `moonshotai/kimi-k2.7-code` | ✓ Working | With vision |
| GLM-5.2 | `zai-org/glm-5.2` | ✓ Working | 1M context |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` | ✓ Working | Default fast model |
| Qwen 3.8 Max | `qwen/qwen3.8-max` | ✓ Working | Autonomous coding |
| Qwen 3.7 Max | `qwen/qwen3.7-max` | ✓ Working | Frontier coding |
| Muse Spark 1.2 Contributor | `meta/muse-spark-1.2-contributor` | ✓ Working | ~95% off pricing |
| Grok 4.5 | `xai/grok-4.5` | ✓ Working | Smart coding model |
| Inkling | `thinkingmachines/inkling` | ✓ Working | Multimodal MoE |

### ✗ Failed Models (1)

| Model Name | Model ID | Status | Error |
|------------|----------|--------|-------|
| Inkling Small | `thinkingmachines/inkling-small` | ✗ Timeout | Request timed out after 90+ seconds |

---

## Test Method

Each model was tested with a simple "Hi" prompt using:
```bash
commandcode -m <model-id> -p --max-turns 1 "Hi"
```

Models that timed out or hit turn limits were retested with:
```bash
commandcode -m <model-id> -p --max-turns 2 "Say hi"
```

---

## Conclusion

Your CommandCode API key is **working correctly** for **10 out of 11** requested models (91% success rate).

The only model that failed was **Inkling Small** (`thinkingmachines/inkling-small`), which consistently timed out after 90+ seconds, suggesting either:
- The model is extremely slow or unavailable
- There may be an API-side issue with this specific model
- Your account may not have access to this particular model

**Recommendation:** Your API key is fully functional. If you need Inkling Small specifically, contact CommandCode support to check model availability.
