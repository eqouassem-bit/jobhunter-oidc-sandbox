"""Start the public, data-free OIDC sandbox on Render.

Sensitive values are read from Render environment variables at process start.
They are NOT committed to Git or printed to logs.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

KEYS = {
    "OIDC_REDIRECT_URI": "redirect_uri",
    "OIDC_COOKIE_SECRET": "cookie_secret",
    "OIDC_CLIENT_ID": "client_id",
    "OIDC_CLIENT_SECRET": "client_secret",
}
METADATA = "https://accounts.google.com/.well-known/openid-configuration"


def config_from_env(environ):
    values = {name: str(environ.get(name, "") or "").strip() for name in KEYS}
    email = str(environ.get("APP_ALLOWED_EMAILS", "") or "").strip()
    ready = all(values.values()) and bool(email)
    if ready:
        ready = (values["OIDC_REDIRECT_URI"].startswith("https://")
                 and values["OIDC_REDIRECT_URI"].endswith("/oauth2callback")
                 and len(values["OIDC_COOKIE_SECRET"]) >= 32)
    return values, email, ready


def write_private_secrets(root, environ):
    """Write a process-local file with owner-only permissions (never log values)."""
    values, email, ready = config_from_env(environ)
    target = Path(root) / ".streamlit" / "secrets.toml"
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lines = [
        'SANDBOX_AUTH_MODE = "google"' if ready else 'SANDBOX_AUTH_MODE = "off"',
        "APP_ALLOWED_EMAILS = " + json.dumps(email if ready else ""),
    ]
    if ready:
        lines.append("")
        lines.append("[auth]")
        lines.extend(
            field + " = " + json.dumps(values[env_name], ensure_ascii=True)
            for env_name, field in KEYS.items()
        )
        lines.append("server_metadata_url = " + json.dumps(METADATA))
    # Ensure files are not readable by other local users.
    old_umask = os.umask(0o077)
    try:
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        target.chmod(0o600)
    finally:
        os.umask(old_umask)
    return ready


if __name__ == "__main__":
    # No secrets are interpolated into the shell or exposed in command args.
    write_private_secrets(Path(__file__).resolve().parent, os.environ)
    port = str(os.getenv("PORT", "10000"))
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        raise SystemExit("Invalid PORT")
    command = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.address=0.0.0.0", "--server.port=" + port,
        "--server.headless=true",
    ]
    raise SystemExit(subprocess.call(command))
