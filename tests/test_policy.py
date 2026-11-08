"""Standalone auth policy tests: no Google account or secrets required."""
import ast
from pathlib import Path
import unittest

from sandbox_auth import GOOGLE_METADATA, allowed_email, oidc_config_ready, identity_authorized


class PolicyTests(unittest.TestCase):
    def test_owner_email_must_be_single_and_explicit(self):
        self.assertEqual(allowed_email({"APP_ALLOWED_EMAILS":"  USER@Example.COM  "}), "user@example.com")
        self.assertEqual(allowed_email({"APP_ALLOWED_EMAILS":"a@example.com,b@example.com"}), "")
        self.assertEqual(allowed_email({}), "")

    def test_configuration_fails_closed(self):
        cfg = {"auth": {
            "redirect_uri":"https://test.example.streamlit.app/oauth2callback",
            "cookie_secret":"x"*48,
            "client_id":"dummy",
            "client_secret":"not-a-real-key",
            "server_metadata_url":GOOGLE_METADATA,
        }}
        self.assertTrue(oidc_config_ready(cfg))
        self.assertFalse(oidc_config_ready({"auth":{"client_id":"dummy"}}))
        cfg["auth"]["redirect_uri"]="http://test.example/oauth2callback"
        self.assertFalse(oidc_config_ready(cfg))

    def test_authorization_enforces_google_verified_expiry_and_allowlist(self):
        good = {"iss":"https://accounts.google.com", "email":"user@example.com", "email_verified":True, "exp":2000}
        self.assertTrue(identity_authorized(good,"user@example.com", now=1000))
        self.assertFalse(identity_authorized(good,"other@example.com", now=1000))
        self.assertFalse(identity_authorized(good,"user@example.com", now=3000))
        self.assertFalse(identity_authorized({**good,"email_verified":False},"user@example.com", now=1000))
        self.assertFalse(identity_authorized({**good,"iss":"evil"},"user@example.com", now=1000))
        self.assertFalse(identity_authorized({**good,"exp":None},"user@example.com", now=1000))

    def test_web_app_is_data_free(self):
        src=(Path(__file__).resolve().parents[1]/"app.py").read_text(encoding="utf-8")
        tree=ast.parse(src)
        imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                imports.update(alias.name for alias in node.names)
            if isinstance(node,ast.ImportFrom):
                imports.add(node.module)
        self.assertEqual(imports,{"streamlit","sandbox_auth"})
        for forbidden in ("DATABASE_URL", "client_secret", "st.write(st.user", "st.json(st.user", "st.user.to_dict"):
            self.assertNotIn(forbidden,src)
        self.assertIn("st.login()",src)
        self.assertIn("st.logout()",src)


if __name__ == "__main__":
    unittest.main()
