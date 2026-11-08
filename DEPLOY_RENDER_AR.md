# دليل تشغيل اختبار Google على Render

هذه الخدمة التجريبية مستقلة تمامًا عن JobHunter AI الأصلي، ولا تتصل بأي قاعدة بيانات.

1. افتح https://dashboard.render.com/ واختر **New → Web Service**.
2. اختر مستودع GitHub العام `eqouassem-bit/jobhunter-oidc-sandbox`.
3. حدّد الفرع `main` ولغة `Python` وخطة `Free`.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python render_start.py`
6. أنشئ الخدمة أولًا **دون تعبئة أسرار OAuth**. ستعمل بوضع معطل وتعرض رسالة إعداد.
7. انسخ عنوان الخدمة الحقيقي المنتهي بـ `.onrender.com`. في Google Cloud Console، أضف كـ **Authorized redirect URI** العنوان نفسه متبوعًا بـ `/oauth2callback`. لا تحذف عنوان التطبيق الأصلي.
8. من Render **Environment** أضف متغيرات الخدمة السرية التالية، مع إخفاء قيمها:
   - `APP_ALLOWED_EMAILS`: عنوان بريد واحد مسموح به.
   - `OIDC_REDIRECT_URI`: الرابط الحقيقي للتجربة `https://YOUR-SERVICE.onrender.com/oauth2callback`.
   - `OIDC_CLIENT_ID`: معرف العميل من Google.
   - `OIDC_CLIENT_SECRET`: سر العميل من Google.
   - `OIDC_COOKIE_SECRET`: سر عشوائي طويل مختلف عن كلمات المرور الأخرى، طوله 32 حرفًا على الأقل (ويُفضّل 64).
9. عند اكتمال المتغيرات وإعادة تشغيل الخدمة، سيُفعَّل Google فقط في **التطبيق التجريبي**. اختبر الدخول بحسابك المصرح به، والحظر لحساب آخر، ثم الخروج.
10. لا تضف إلى Render التجريبي أي `DATABASE_URL` أو مفاتيح Adzuna أو بيانات أشخاص أو كلمات مرور للتطبيق الأصلي.

بقيت إعدادات OIDC والبيانات الشخصية خارج GitHub. يحوّل `render_start.py` متغيرات الخدمة سرًا إلى `.streamlit/secrets.toml` في حاوية التشغيل، بصلاحيات 0600. وهذا الملف مستثنى من Git بواسطة `.gitignore`. لا تعرضه في Screenshots أو Logs.

ملاحظة: الخطة المجانية قد تُوقِف الخدمة تلقائيًا بعد عدم النشاط، كما أن إتاحة الخطط قد تتغير. لا تفعّل تسجيل الدخول في التطبيق الأصلي قبل اختبار القبول/الرفض والخروج وموافقتك الصريحة.
