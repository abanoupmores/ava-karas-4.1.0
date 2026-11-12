# FIREBASE_MIGRATION — خطوات يدوية (لا شيء يُنشر تلقائيًا)

المشروع: `youth-family-c039e` (لم يتغير). **لا ترحيل بيانات ولا حذف.** كل شيء إضافي.

## 1) نشر القواعد (إلزامي لتعمل الشاشات الجديدة)
Firebase Console ← Firestore Database ← Rules ← الصق `firestore.rules` كاملًا ← Publish.
القواعد القديمة كما هي حرفيًا؛ أُضيف: دالة `votePts()` + فرع جديد في تحديث `members` + 4 كتل (`hymnFolders`, `hymns`, `polls`, `pollVotes`). `config` يغطي `app_update` و`weekly`.
قبل النشر: جرّب في Rules Playground أو Emulator (لم يُختبر هنا — انظر TEST_REPORT).
بدون النشر: الشاشات القديمة تعمل، والجديدة تعرض «مفيش صلاحية: انشر القواعد».

## 2) Collections/Documents الجديدة (تُنشأ تلقائيًا عند أول استخدام)
| المسار | الحقول |
|---|---|
| `hymnFolders/{auto}` | name, order, pinned, deleted, deletedAt, createdAt, updatedAt, createdBy, createdByName |
| `hymns/{auto}` | name, lyrics, folderId, originalFolderId, audioUrl, audioPath, imageUrl, image(dataURL مضغوط), deleted, deletedAt, createdAt, updatedAt, createdBy, createdByName |
| `polls/{auto}` | question, options[], allowMultiple, choir, isActive, deleted, total, final{counts,total}, createdAt, endedAt, createdBy, createdByName |
| `pollVotes/{pollId_memberId}` | pollId, memberId, name, choir, choices[], pts, at |
| `config/app_update` | version, notes, url, sha256, isActive, updatedAt, by |
| `config/weekly` | enabled, title, day(0=الأحد), time, choir, weeks, lastGen, updatedAt, by |
| `members/{id}` حقل جديد | `lastVotePoll` (اختياري) |
| `events/{id}` حقول جديدة | `weekly`, `series` (اختيارية) |
| `adjustments/{id}` حقل جديد | `kind:'reset'` عند تصفير النقاط (اختياري) |

## 3) اختياري: رفع ملفات MP3
1. Console ← Storage ← Get started (قد يتطلب خطة Blaze حسب سياسة Firebase).
2. Storage ← Rules ← الصق `storage.rules` ← Publish (يعتمد على `users/{uid}.role == 'servant'`).
بدون ذلك: استخدم رابط صوت https مباشر (Drive/Dropbox يُحوَّلان تلقائيًا). رسالة الخطأ في التطبيق تشرح الحالة ولا يُحفظ شيء عند فشل الرفع.

## 4) اختياري: نقطة التصويت
`config/main.votePts` (رقم 0–5). غير موجود = 1. القيمة 0 تعطّل النقطة. (يمكن إضافتها من Console؛ لا توجد واجهة لها حاليًا.)

## 5) ملاحظات حجم
صورة الترنيمة المرفوعة تُحفظ مضغوطة (≈360px) داخل مستند الترنيمة، والتطبيق يحمّل حتى 1500 ترنيمة. للأعداد الكبيرة جدًا فضّل رابط الصورة.

## 6) تراجع (Rollback)
حذف الشاشات الجديدة لا يتطلب تغيير بيانات: ارجع لنسخة Git `e8ebf9f` (baseline v3.0.0) واترك الـ collections الجديدة فارغة/مهملة. القواعد الجديدة إضافية فقط فلا تؤثر على النسخة القديمة.
