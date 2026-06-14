# Key Rotation

## Service API key (`API_KEY_HASHES`)

This is the key callers present to authenticate against the API.

1. Generate a new key:

```bash
python scripts/rotate_api_key.py
```

2. Add the hash to `API_KEY_HASHES` in the secret manager.
3. Deploy the updated secret.
4. Confirm the new key works.
5. Remove the old hash from the secret manager.
6. Deploy again and verify the old key fails.

## LLM provider key (`NVIDIA_API_KEY`)

This is the upstream credential the LLM analysts use. The code reads `NVIDIA_API_KEY` (or `OPENAI_API_KEY` as a fallback) from the environment.

1. Provision a new key with the LLM provider.
2. Set `NVIDIA_API_KEY` in the secret manager and deploy.
3. Confirm the provider is reachable via `GET /llm/status`, then run a live check with `POST /llm/test`.
4. Revoke the old key at the provider.

Never commit raw keys or production `.env` files.
