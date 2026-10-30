# تطبيقات القرآن

تطبيقات قرآنية تعليمية من منصة أفق، عربية ومناسبة للهاتف، تعمل بلا إنترنت بعد أول زيارة.
كل الآيات من نص المصحف الموثّق في `data/quran.json` (الرسم العثماني، رواية حفص، 6236 آية؛ المصدر في `data/README.md`).

- الصفحة الرئيسية: `index.html` (تُبنى من `apps.json`).
- تطبيق جديد: `python3 tools/new_app.py <slug> "<العنوان>" "<الوصف>"`.
- الفحص: `python3 tools/quran_check.py` و`node tools/app_check.mjs`.
- الخريطة: `python3 tools/graphify.py /tmp/graphify.html`.

قواعد العمل في `CLAUDE.md`.
