# Local AI model setup (team standard)

SICO AI runs on a local [Ollama](https://ollama.com) server. To make results comparable,
every machine must run **the same model build**:

| Item | Required value |
|---|---|
| Model | `qwen3:4b-instruct` |
| Model ID (first 12 chars of the digest, shown by `ollama list`) | `0edcdef34593` |
| Ollama version | `0.40.17` |

These values live in `backend/ai_onboarding/llm_config.py` (`PINNED_MODEL`,
`PINNED_MODEL_DIGEST`, `PINNED_OLLAMA_VERSION`).

## Setup

1. Install Ollama `0.40.17` and make sure it is running.
2. Pull the model, and optionally remove any models the project does not use:
   ```
   ollama pull qwen3:4b-instruct
   ollama list
   ```
   Check that the `ID` column shows `0edcdef34593` for `qwen3:4b-instruct`.
3. Start the stack: `docker compose up -d`. AI is enabled by default in `docker-compose.yml`.
   - The backend reaches Ollama at `http://192.168.65.254:11434`, which is the host as seen from Docker Desktop.
   - If your host address differs, set `LOCAL_AI_BASE_URL` in a `.env` file next to `docker-compose.yml`.
   - The URL must be an IP address: hostnames such as `host.docker.internal` are rejected by design.
4. Verify:
   ```
   docker exec backend poetry run python manage.py check_ai_model
   ```
   Every line should say `OK`. The same check runs at every backend start and is printed in
   `docker logs backend`.

## What the check does

- The check never blocks the platform. It only warns.
- It warns when:
  - Ollama is unreachable;
  - the Ollama version differs from the standard;
  - the pinned model is missing or has a different digest;
  - any `LOCAL_AI_MODEL_*` variable points to another model.
- Use `--strict` to make it fail. This is useful in scripts.

## Why this model

The model was measured with the SICO AI Next quality drafts (activities 4–16) on four frameworks.

| Framework | Drafts accepted |
|---|---|
| ISO/IEC 27001:2022 | 13/13 |
| NIST CSF 2.0 | 13/13 |
| PCI DSS 4.0.1 | 13/13 |
| NCA ECC | 13/13 |

Reject rate was 2%.

`qwen2.5:7b-instruct` was also tested on a laptop with a 4 GB GPU and 8 GB RAM:

| Model | Layers on GPU | Speed |
|---|---|---|
| `qwen3:4b-instruct` | 26/37 | 14.1 tokens/s |
| `qwen2.5:7b-instruct` | 12/29 | 3.7 tokens/s |

The 7B model was about four times slower, and its first load crashed. The standard model must run on
the weakest team machine. A larger model can still be used for a single capability through
`LOCAL_AI_MODEL_<CAPABILITY>`; the check will report it.

## Changing the standard

Change it for the whole team in one pull request, which must include:

- the three constants in `llm_config.py`;
- `LOCAL_AI_MODEL_DEFAULT` in `docker-compose.yml`;
- this file;
- the measurement results for the new model.
