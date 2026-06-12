# API Key Rotation

1. Generate a new key:

```bash
python scripts/rotate_api_key.py
```

2. Add the hash to `API_KEY_HASHES` in the secret manager.
3. Deploy the updated secret.
4. Confirm the new key works.
5. Remove the old hash from the secret manager.
6. Deploy again and verify the old key fails.

Never commit raw keys or production `.env` files.
