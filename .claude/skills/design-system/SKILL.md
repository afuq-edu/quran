---
name: design-system
description: نظام التصميم الموحّد لتطبيقات القرآن (الألوان والخطوط القرآنية والمكونات، فاتح وداكن، RTL). استعملها عند تصميم واجهة أو تعديل شكل تطبيق أو عند «/design-system».
---

# /design-system — شكل واحد لكل التطبيقات

كل تطبيق يربط `assets/design.css` و`assets/quran.js` ويبني بهما. اقرأ `assets/design.css` قبل أي تصميم.

## الأساس
- **الألوان** متغيرات فقط: `--bg --surface --surface-2 --ink --muted --line --brand --brand-soft --gold --gold-soft --ok --warn --bad`.
  لا تكتب لونًا مباشرًا في تطبيق؛ إن احتجت لونًا جديدًا فأضفه متغيرًا في الوضعين (الفاتح والداكن) في `design.css`.
- **الخطوط:** `--font-quran` (Amiri Quran) للآيات فقط، و`--font-ui` (Tajawal) لكل ما عداها. حجم الآية `--ayah-size`.
- **الوضعان:** يتبع الجهاز تلقائيًا، وزر 🌓 يحفظ الاختيار: `Quran.Theme.init(document.getElementById('theme'))`.
- **الأرقام:** أرقام الآيات والسور بالأرقام العربية المشرقية `Quran.digits(n)`.

## المكونات
`.app-bar` (شريط علوي فيه زر الرجوع والعنوان وزر الوضع)، `.page` (عرض أقصى 760 px)، `.card`، `.grid`، `.row`، `.stack`،
`.btn` و`.btn.primary` و`.icon-btn` (44 px على الأقل)، `.chip` و`.chip.gold`، `.surah-header`، `.basmala`، `.ayah`
مع `<span class="ayah-num">` بعد كل آية، و`.ayah.active` للآية الحالية.

## قواعد
- عربي `lang="ar" dir="rtl"`، والمسارات والكود داخل `<code>` أو `.ltr`.
- الهاتف أولًا: صمّم على 360 px ثم وسّع. لا تمرير أفقي. منطقة اللمس 44 px.
- التباين مقروء في الوضعين، وحالة تركيز ظاهرة (`:focus-visible`)، و`aria-label` لكل زر أيقونة.
- البسملة تُعرض قبل كل سورة إلا الفاتحة (هي آيتها الأولى) والتوبة.
- لا تحذف مكوّنًا من `design.css` تستعمله تطبيقات أخرى؛ ابحث عنه أولًا (`grep -r "اسم-الصنف" apps/`).
- بعد أي تعديل على `design.css` شغّل `python3 tools/pwa.py --all` (لتحديث النسخ المحفوظة على الهواتف) ثم `node tools/app_check.mjs`.
