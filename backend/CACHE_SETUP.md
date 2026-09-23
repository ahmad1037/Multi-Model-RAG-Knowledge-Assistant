# Docker model cache

The backend and worker run as `appuser`. Their shared Hugging Face volume must be
mounted at `/home/appuser/.cache/huggingface`, not under `/root`. The image creates
this directory with appuser ownership for new volumes. Compose also places uv's
disposable cache at `/tmp/uv-cache`.

For an existing volume created by an older root-running image, migrate ownership
once from the repository root before starting the updated services:

```powershell
docker compose run --rm --no-deps --user root backend chown -R appuser:appgroup /home/appuser/.cache/huggingface
docker compose up -d --build backend
```

If a worker is already deployed, rebuild/recreate it with `docker compose up -d
--build worker` as well. The ownership migration preserves downloaded models and
does not delete the model cache or database volume. Application processes continue
to run as appuser; root is used only for the one-time volume ownership migration.
