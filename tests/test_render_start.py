"""Regression checks for safe host startup config and owner-only file permissions."""
import ast
import os
from pathlib import Path
import tempfile
import unittest
from render_start import config_from_env, write_private_secrets

VALID = {
    "APP_ALLOWED_EMAILS": "only-owner@example.com",
    "OIDC_REDIRECT_URI": "https://jobhunter-oidc-sandbox.onrender.com/oauth2callback",
    "OIDC_CLIENT_ID": "dummy-id",
    "OIDC_CLIENT_SECRET": "dummy-secret",
    "OIDC_COOKIE_SECRET": "a"*48,
}


class TestRenderStart(unittest.TestCase):
    def test_missing_secrets_do_not_enable_login(self):
        with tempfile.TemporaryDirectory() as tmp:
            ready = write_private_secrets(tmp, {})
            self.assertFalse(ready)
            conf = (Path(tmp)/".streamlit"/"secrets.toml").read_text()
            self.assertIn('SANDBOX_AUTH_MODE = "off"', conf)
            self.assertNotIn("[auth]", conf)

    def test_config_has_expected_fields_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            ready = write_private_secrets(tmp, VALID)
            self.assertTrue(ready)
            file = Path(tmp)/".streamlit"/"secrets.toml"
            contents = file.read_text()
            self.assertIn('SANDBOX_AUTH_MODE = "google"', contents)
            self.assertIn("[auth]", contents)
            self.assertIn("https://accounts.google.com/.well-known/openid-configuration", contents)
            self.assertEqual(file.stat().st_mode & 0o777, 0o600)

    def test_reject_invalid_redirect(self):
        changed = dict(VALID, OIDC_REDIRECT_URI="http://localhost:8501/oauth2callback")
        self.assertFalse(config_from_env(changed)[2])

    def test_no_secrets_baked_into_source(self):
        source=(Path(__file__).resolve().parents[1]/"render_start.py").read_text()
        ast.parse(source)
        self.assertNotIn("DATABASE_URL", source)
        self.assertNotIn("ADZUNA_APP_KEY", source)


if __name__=="__main__":
    unittest.main()
