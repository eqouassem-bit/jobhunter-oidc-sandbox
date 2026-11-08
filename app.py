"""JobHunter AI - zero-data, separate Google OIDC login sandbox.

No access to the main project, Supabase, private profiles or any job history.
"""
import streamlit as st
from sandbox_auth import allowed_email, oidc_config_ready, identity_authorized

st.set_page_config(page_title="JobHunter AI | Google Login Test", page_icon="🔐", layout="centered")
st.title("🔐 Google OAuth / OIDC — اختبار معزول")
st.write("هذا اختبار هوية فقط. لا توجد بيانات وظائف أو سِيَر ذاتية أو اتصال بقاعدة بيانات.")

try:
    configuration = st.secrets
    enabled = str(configuration.get("SANDBOX_AUTH_MODE", "off") or "").strip().lower() == "google"
    owner = allowed_email(configuration)
    configured = oidc_config_ready(configuration)
except Exception:
    enabled, owner, configured = False, "", False

if not enabled:
    st.info('التجربة غير مفعّلة. ضع SANDBOX_AUTH_MODE = "google" في Secrets الخاصة بتطبيق الاختبار فقط.')
    st.stop()

if not (configured and owner):
    st.error("الإعداد غير مكتمل. أضف بريدًا واحدًا مخولًا وحقول [auth] الخمسة داخل Secrets الخاصة بالاختبار.")
    st.stop()

try:
    signed_in = bool(st.user.is_logged_in)
except (AttributeError, RuntimeError):
    signed_in = False

if not signed_in:
    st.write("يظهر زر الدخول فقط حتى تكتمل المصادقة عبر Google.")
    if st.button("🔐 Entrar con Google", type="primary"):
        st.login()
    st.stop()

claims = {
    "iss": st.user.get("iss"),
    "email": st.user.get("email"),
    "email_verified": st.user.get("email_verified"),
    "exp": st.user.get("exp"),
}
if not identity_authorized(claims, owner):
    st.error("تم رفض الدخول: الحساب غير مخوّل أو غير موثق أو انتهت صلاحية الجلسة.")
    if st.button("Cerrar sesión", key="logout_rejected"):
        st.logout()
    st.stop()

st.success("✅ Google OIDC: تم التحقق من الهوية والحساب المصرح له.")
st.caption("لا تُعرض بيانات الهوية ولا يتم حفظ أي رموز أو كلمات مرور.")
if st.button("Cerrar sesión", key="logout_allowed"):
    st.logout()
