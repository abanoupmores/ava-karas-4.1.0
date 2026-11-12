# اختبارات الدخان (بدون Firebase حقيقي)
تستبدل Firebase/Capacitor بـ stub في الذاكرة (`stubs/firebase.js`) وتشغّل الواجهة الحقيقية في Chromium.
لا تختبر Firestore Rules (تحتاج Firebase Emulator).
1. عدّل `__ROOT__` في `build.mjs` و`unit.mjs` إلى مسار المشروع، ومسار esbuild حسب جهازك.
2. `node build.mjs` ثم انسخ `www/` إلى مجلد اختبار وقدّمه على `http://localhost:8765`.
3. `python3 smoke_ui.py` (Playwright) و`node unit.mjs`.

## اختبارات 4.1.0 (تعمل مباشرة بـ node، بلا حزم ولا شبكة)
- `node tests/pts.test.mjs` — منطق النقاط النقي (`src/pts.js`).
- `node tests/admin-worker.test.mjs` — منطق المهمة الإدارية على قاعدة/Auth وهميين.
- `node tests/tx-logic.test.mjs` — تسلسل Transaction (حضور يدوي، تكرار، إلغاء، ترحيبية) فوق stub؛ يحاكي المنطق ولا يستورد `main.js`.
- لا تختبر Firestore Rules ولا الواجهة؛ هذه تحتاج Firebase Emulator ومتصفح.
