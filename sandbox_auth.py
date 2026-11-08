"""Single-owner Google OIDC authorization policy, without credentials or personal data."""
import hmac
import time

GOOGLE_METADATA = "https://accounts.google.com/.well-known/openid-configuration"


def allowed_email(secrets):
    """Require exactly one authorized owner email supplied by private Secrets."""
    try:
        raw = str(secrets.get("APP_ALLOWED_EMAILS", "") or "").strip()
    except (AttributeError, TypeError):
        return ""
    items = [part.strip().casefold() for part in raw.split(",") if part.strip()]
    if len(items) != 1:
        return ""
    email = items[0]
    if "@" not in email or " " in email or email.startswith("@") or email.endswith("@"):
        return ""
    return email


def oidc_config_ready(secrets):
    """Validate configuration shape without printing or storing secrets."""
    try:
        cfg = secrets.get("auth", {})
        fields = ("redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url")
        if not all(str(cfg.get(k, "") or "").strip() for k in fields):
            return False
        uri = str(cfg.get("redirect_uri", ""))
        return (
            uri.startswith("https://")
            and uri.endswith("/oauth2callback")
            and cfg.get("server_metadata_url") == GOOGLE_METADATA
            and len(str(cfg.get("cookie_secret", ""))) >= 32
        )
    except (AttributeError, TypeError, ValueError, OSError):
        return False


def identity_authorized(identity, owner_email, now=None):
    """Require Google issuer, verified email, allowlist match, and unexpired ID token."""
    if not isinstance(identity, dict) or not owner_email:
        return False
    email = str(identity.get("email", "") or "").strip().casefold()
    verified = identity.get("email_verified") in (True, "true", "True")
    issuer = str(identity.get("iss", "") or "")
    if not (verified and issuer in ("https://accounts.google.com", "accounts.google.com") and email):
        return False
    try:
        expiry = float(identity["exp"])
    except (KeyError, ValueError, TypeError):
        return False
    if expiry <= (time.time() if now is None else now):
        return False
    return hmac.compare_digest(email, owner_email)
