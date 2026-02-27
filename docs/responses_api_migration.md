# Migrating to GPT-5 Series Models (Responses API)

GPT-5 series models (gpt-5, gpt-5-mini, gpt-5-nano, etc.) use OpenAI's
**Responses API** instead of the Chat Completions API.  The two APIs return
LLM output in different shapes, so every project that calls an LLM through
`aiweb_common` needs a small set of changes to work with both.

## What changed

| | Chat Completions API | Responses API |
|---|---|---|
| **Models** | gpt-4o, gpt-4o-mini, etc. | gpt-5, gpt-5-mini, gpt-5-nano, etc. |
| **`response.content` type** | `str` | `list[dict]` — e.g. `[{"type": "output_text", "text": "..."}]` |
| **`ChatOpenAI` kwarg** | *(default)* | `use_responses_api=True` |
| **Optional kwarg** | — | `reasoning_effort="low" \| "medium" \| "high"` |

The critical breakage: any code that does `response.content.strip()` (or
any other string method) crashes with `'list' object has no attribute 'strip'`
when running against a Responses API model.

## Migration steps

### 1. Update dependencies

Make sure you are on at least these versions (or newer):

```
langchain-openai >= 1.1.0
openai >= 2.20.0
```

The `use_responses_api` kwarg on `ChatOpenAI` was added in langchain-openai
1.1.0.  Older versions will raise a `TypeError`.

### 2. Detect Responses API models

Add a helper that decides whether a model name requires the Responses API.
In Grant_Editor this lives in `workflow.py`, but you can put it wherever your
project initialises its LLM:

```python
import re
from re import Pattern

_GPT5_PATTERN: Pattern[str] = re.compile(r"^gpt-?5", re.IGNORECASE)

def _is_responses_api_model(model_name: str) -> bool:
    """Return True if the model should use the Responses API."""
    return bool(_GPT5_PATTERN.match(model_name))
```

### 3. Pass the flag to `_init_openai`

`WorkflowHandler._init_openai()` already accepts `use_responses_api` and
`reasoning_effort`.  Wire them up in your workflow `__init__`:

```python
from your_project.config import REASONING_EFFORT   # e.g. "low"

class MyWorkflow(WorkflowHandler):
    def __init__(self, llm_settings, ...):
        super().__init__()
        _use_responses = _is_responses_api_model(llm_settings.model)
        self._init_openai(
            openai_compatible_endpoint=llm_settings.endpoint,
            openai_compatible_key=llm_settings.api_key,
            openai_compatible_model=llm_settings.model,
            name="my_workflow",
            use_responses_api=_use_responses,
            reasoning_effort=REASONING_EFFORT if _use_responses else None,
        )
```

If you don't need reasoning effort control, you can omit that kwarg entirely.

### 4. Use `extract_response_text` for all LLM output

This is the most important step.  **Every place** your code reads text from
an LLM response must go through the shared helper:

```python
from aiweb_common.WorkflowHandler import extract_response_text
```

**Before (breaks on Responses API):**
```python
response = self.llm_interface.invoke(assembled)
text = response.content.strip()
```

**After (works with both APIs):**
```python
response = self.llm_interface.invoke(assembled)
text = extract_response_text(response.content)
```

The function handles three cases:
- `str` — returns it stripped (Chat Completions API)
- `list[dict]` — joins the `"text"` values from each content block (Responses API)
- anything else — falls back to `str()` conversion

### 5. Audit your codebase

Search for every place `.content` is accessed on an LLM response and treated
as a string:

```bash
grep -rn '\.content\.strip\|\.content\.\(split\|lower\|upper\|replace\|startswith\|endswith\)' \
    --include='*.py' your_project/
```

Also check for patterns like:
```python
# These all assume .content is a string — all need extract_response_text()
f"Result: {response.content}"
len(response.content)
if "keyword" in response.content:
json.loads(response.content)
```

### 6. If you use `check_content_type`

`WorkflowHandler.check_content_type()` has been updated to handle the
Responses API list format internally.  If you pass an `AIMessage` to it, it
now returns the correct extracted string for both APIs.  No changes needed on
the caller side.

### 7. Define `REASONING_EFFORT` in your config

GPT-5 series models support a `reasoning_effort` parameter.  Add a constant
to your project's config:

```python
# Valid values: "low", "medium", "high"
REASONING_EFFORT = "low"
```

This is optional — omitting it uses the model's default.  Use `"low"` for
fast, cheap calls (rewrites, classification) and `"high"` for complex
analysis.

## Checklist

- [ ] `langchain-openai >= 1.1.0` and `openai >= 2.20.0` in requirements
- [ ] Model detection helper (`_is_responses_api_model` or equivalent)
- [ ] `_init_openai()` calls pass `use_responses_api` and `reasoning_effort`
- [ ] **All** `response.content.strip()` replaced with `extract_response_text(response.content)`
- [ ] **All** other direct string operations on `response.content` go through `extract_response_text()`
- [ ] `REASONING_EFFORT` config constant added
- [ ] Tested with both a gpt-4o model and a gpt-5 model
