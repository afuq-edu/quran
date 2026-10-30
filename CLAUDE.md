# تطبيقات القرآن — قواعد ثابتة للعمل على المستودع

مستودع تطبيقات قرآنية تعليمية (منصة أفق)، صفحات ثابتة تُنشر على GitHub Pages في `https://afuq-edu.github.io/quran/`.
لا خطوة بناء: كل تطبيق صفحة HTML تعمل كما هي.

## البنية
- `apps.json` — **فهرس التطبيقات** (slug، العنوان، الوصف، الحالة draft/ready، الوسوم). منه تُبنى `index.html` والخريطة.
- `apps/<slug>/` — تطبيق واحد: `index.html` وملفاته، و`manifest.webmanifest` و`sw.js` و`icon.svg` من `tools/pwa.py`.
- `assets/design.css` و`assets/quran.js` — التصميم والمساعدات المشتركة (مهارة design-system).
- `data/quran.json` — نص المصحف الموثّق، **المرجع الوحيد للآيات**. لا يُعدَّل (انظر `data/README.md`).
- `templates/app/` — قالب التطبيق الجديد. `tools/` — الأدوات (لكل أداة شرح في أولها).

## القواعد
1. الآيات من `Quran.load()` دائمًا، لا تُكتب باليد. قبل أي رفع فيه آيات: `python3 tools/quran_check.py` بلا أخطاء.
2. تطبيق جديد: `python3 tools/new_app.py ...` (مهارة new-app)، لا تنسخ المجلدات يدويًا.
3. بعد تعديل تطبيق أو ملف مشترك: `python3 tools/pwa.py --all` ثم `node tools/app_check.mjs` وانظر صور الهاتف.
4. عربي RTL، الهاتف أولًا (360 px)، فاتح وداكن، أزرار 44 px، ألوان `design.css` فقط.
5. بعد تعديل `apps.json` باليد: `python3 tools/new_app.py --index`.
6. الملفات الكبيرة (صوت، صور كثيرة): راقب الحجم بـ `/graphify`؛ حد GitHub Pages ‏1 GB.

## المهارات
`/graphify` خريطة المشروع · `/new-app` تطبيق جديد · `/app-check` فحص في المتصفح · `/quran-text-check` سلامة الآيات ·
`/design-system` التصميم الموحّد · `/pwa-offline` العمل بلا إنترنت.
