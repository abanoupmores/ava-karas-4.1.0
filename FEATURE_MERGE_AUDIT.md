# FEATURE_MERGE_AUDIT — الإصدار 4.1.0

> يثبت هذا الملف أن وظائف 4.0.0 محفوظة، وما الذي تغيّر، وما الذي اختُبر فعليًا. التفاصيل والقيود: `REPORT_4.1.0.md`. النشر: `DEPLOY_4.1.0.md`.

## أ) الحفاظ على الوظائف القديمة — الدليل
- جرد آلي (نص المصدر): **89 دالة `window.*` و24 صفحة `PG.*` في 4.0.0 ← كلها موجودة في 4.1.0، المفقود = صفر.** المضاف: 12 دالة و`PG.chat`.
- كتل القواعد القديمة كلها موجودة: secrets, users, members, events, attendance, adjustments, notifs, config, hymnFolders, hymns, polls, pollVotes.
- لم يُغيَّر: Firebase Project، `toMail`، نظام الدخول، الصفحة الرئيسية (أُضيف مدخل «الشات» فقط)، الترانيم والمجلدات والسلة، التصويت، الإشعارات، التقارير، الإحصائيات، الجداول، الخلفيات، التحديثات، التذكيرات، سكربتات البناء.
- لا حذف ولا تصفير لأي بيانات؛ كل الحقول الجديدة اختيارية.

## ب) ما تم **تعديله** داخل الملفات القائمة (وليس حذفه)
| الموضع | التعديل |
|---|---|
| `calc` | يستدعي `calcAuto` من `src/pts.js` (نفس المعادلة حرفيًا، مغطاة باختبارات) |
| `checkIn` | Transaction + `lastAtt` + خيارات الحضور اليدوي |
| `ma` / `ra` | نافذة اختيار النقاط؛ الإلغاء يقرأ النقاط المسجّلة فعلًا |
| `sm` | مزامنة حساب المخدوم المفعّل + منع تعارض الأرقام + حقول الأهلية للجدد |
| `mkUser` | حقلا `welcomeEligible/welcomePaid` للمخدوم الجديد |
| `pf` / `spf` / الملف الشخصي للخادم | صورة + اسم + هاتف |
| `PG.set` / `sc` | إعداد `welcomePts` |
| `onAuthStateChanged` | شاشة تغيير الباسورد الإجباري عند `mustChangePw` |
| `out` | إيقاف مستمعي الشات عند الخروج |
| `firestore.rules` | تشديد users/members/attendance/adjustments + قواعد الشات + `adminRequests` (النسخة القديمة: `firestore.rules.4.0.0.bak`) |

## ج) ما اختُبر فعليًا / ما لم يُختبر
| البند | الحالة |
|---|---|
| منطق النقاط (23)، المهمة الإدارية (20)، تسلسل Transaction على stub (16)، فحص صياغة JS، جرد الدوال | ✅ نجح |
| بناء `esbuild`، Android APK، Windows | ❌ لم يُنفَّذ (لا شبكة/SDK) |
| قواعد Firestore على Emulator | ❌ لم يُنفَّذ |
| تسجيل الدخول (خادم/مخدوم)، إنشاء/تعديل/حذف مخدوم، QR، حضور يدوي حقيقي، إلغاء، تصفير، ترانيم، تصويت، إشعارات، تقارير، جداول، إعدادات | ❌ لم تُختبر على Firebase حقيقي — محفوظة هيكليًا فقط (أ) |
| تفعيل الحساب، الدخول بـ123456، إجبار التغيير، الشات (عزل الكورالات/الخدام)، بقاء الرسائل، ملف الخادم، الترحيبية | ❌ لم تُختبر على Firebase حقيقي — المنطق المرتبط بالترحيبية والحضور مختبر على stub فقط |

---

# (أرشيف) تدقيق دمج Silent Monk — الإصدار 4.0.0

# FEATURE_MERGE_AUDIT — Abba Karas ⟵ Silent Monk

> المشروع الأساسي: `abba-karas-pc-main` (Capacitor + Firebase JS SDK + Electron) — Firebase `youth-family-c039e`.
> التطبيق المرجعي: `base.apk` (`com.example.smchoir`، Kotlin + Jetpack Compose + Firebase Android SDK).
> التاريخ: 2026-11-08.

## 0. طريقة التحليل (وحدودها بصراحة)

| الأداة المطلوبة | المتاح فعليًا | البديل المستخدم |
|---|---|---|
| JADX / APKTool | غير متوفرين (لا شبكة لتنزيلهما) | محلل DEX كتبته بنفسي (Python): قراءة `string_ids / type_ids / method_ids / field_ids / class_defs` + مسح الـ opcodes للحصول على `const-string` والـ `invoke` والـ `iget/iput` لكل method |
| AndroidManifest | تم فكه (binary XML → string pool) | الصلاحيات والـ receivers والـ providers |
| Resources | الـ APK مضغوط بـ R8 + resource shrinking (أسماء ملفات مبهمة) | استُخدمت نصوص الواجهة المباشرة من الـ DEX |

**ما تم التحقق منه:** أسماء الكلاسات والحقول والـ collections ونصوص الواجهة وتسلسل الاستدعاءات داخل كل دالة.
**ما لم يتم:** لم أحصل على كود Kotlin مقروء (control flow كامل)، فكل ما يعتمد على شروط معقدة موسوم بـ **Unverified** أدناه ولم يُنقل كأنه مؤكد.

الـ APK مبني بـ R8: كلاسات التطبيق الحقيقية 7 فقط بأسمائها (`FolderItem, Hymn, MainActivity, PollQuestion, RehearsalReminderReceiver, ServiceSchedule, UserData`) والباقي (≈139 كلاس UI/Firestore) متعتّم بأسماء قصيرة، وتم تتبعه من النصوص ومراجع Firestore.

---

## 1. Existing Features (Abba Karas) — كلها تبقى كما هي

| المجال | الموجود فعليًا في `src/main.js` |
|---|---|
| الحسابات | تسجيل مخدوم/خادم (كود الخادم يتحقق منه Firestore Rules عبر `secrets/servant`)، 5 كورالات، بيانات (اسم، تليفون، ميلاد، صورة)، ربط `users.memberId` ↔ `members` |
| الحضور | QR (المخدوم يمسح كود الحدث `KC\|id`، الخادم يمسح كود المخدوم `KM\|id`)، حضور يدوي، إلغاء حضور، سجل حضور المخدوم (آخر 15) |
| النقاط | فتح قبل البروفة (حتى 30د)، 5 نقاط في الميعاد، −1 كل 5د، صفر بعد 30د، قفل بعد ساعة؛ إضافة/خصم يدوي بسبب + إشعار؛ إعدادات قابلة للتعديل في `config/main` |
| الأحداث | بروفة/حفلة/نشاط + كورال مستهدف + إشعار للمخدومين |
| التقارير | نسبة الحضور، حلقة %، تقرير أسبوعي، افتقاد (< حد)، استحقاق حفلات/صولو |
| الإشعارات | `notifs` داخل التطبيق + محلية: تذكير قبل الحدث بساعة/يوم، أعياد الميلاد، تقرير الثلاثاء 9ص |
| التصميم | هوية كورال الأنبا كاراس، 6 خلفيات أرثوذكسية، آيات التسبيح، RTL |
| المنصات | Android (Capacitor) + Windows (Electron portable/nsis) |
| Collections | `users, members, events, attendance, adjustments, notifs, config, secrets` |

## 2. Extracted Features (Silent Monk) — ما ثبت فعليًا من الـ APK

### 2.1 نماذج البيانات (مؤكدة من الكلاسات وتوقيعات الـ constructors)
- `Hymn(id, name, lyrics, imageUrl, audioUrl, originalFolder, isDeleted)`
- `FolderItem(name, order, pinned, isDeleted)`
- `PollQuestion(id, question, options[], votes{}, votedUsers[], userChoices{}, isActive, allowMultipleAnswers, createdAt)`
- `ServiceSchedule(id, title, date, time, description, type, timestamp, isWeeklyRehearsal, legacyWeeklyRehearsal, dayOfWeek)`
- `UserData(uid, name, email, username, role, code, canViewDetails, profileImage, choirType, points)`

### 2.2 Firestore (مؤكدة من استدعاءات `collection()/document()/whereEqualTo()`)
`Users, Folders (+ Hymns كمجموعة فرعية), Polls, AttendanceLogs, Schedules, AppConfig/app_update`.
ملاحظة Firestore POJO: خاصية Kotlin `isDeleted` تُحفظ باسم الحقل `deleted`.
`AttendanceLogs/{date}_{choir}` = `{ records{uid:true}, timestamps{}, timestampMillis{}, awardedPoints{}, penaltyApplied, date, choirType }`.
`AppConfig/app_update` = `{ version, notes, apkUrl, apkHash, updatedAt, isActive }`.

### 2.3 الوظائف
| # | الميزة | الدليل | الحالة |
|---|---|---|---|
| A1 | مجلدات ترانيم: إضافة، تعديل الاسم، تثبيت في الأعلى، ترتيب (سحب/drag handle)، بحث | نصوص: «إضافة فولدر جديد»، «ترتيب الفولدرات»، «بحث عن فولدر»، حقول `order/pinned` | **Verified** |
| A2 | ترانيم: إضافة/تعديل (الاسم، الكلمات، رابط صوت، رابط صورة)، بحث، تحديد متعدد، نقل للسلة | شاشات `add_hymn / edit_hymn / hymn_player / folder_details` + نصوص | **Verified** |
| A3 | مشغل صوت + تحويل روابط Google Drive/Dropbox لروابط مباشرة | مراجع `docs.google.com/uc?export=download&id=`, `dl=0 → raw=1`, `AudioPlayer` | **Verified** |
| A4 | رفع MP3/صورة من الجهاز | استخدام Cloudinary (unsigned preset) | **Verified لكن لن يُنقل** (حساب خارجي للتطبيق الآخر) |
| A5 | سلة المحذوفات: ترانيم ومجلدات، استعادة، «السلة فارغة تماماً»، تأكيد الحذف | شاشة `trash_screen` + `originalFolder` | **Verified** (تفاصيل الاستعادة مستنتجة من `originalFolder`) |
| B1 | تصويت: سؤال + خيارات ديناميكية + سماح بأكثر من إجابة + نشر + إنهاء وإخفاء + شاشة إدارة | `polls_admin`، «إنشاء تصويت»، «السماح باختيار أكثر من إجابة؟»، «إنهاء التصويت وإخفاؤه» | **Verified** |
| B2 | منع التصويت المكرر + +1 نقطة للمصوّت | Transaction على `Polls` و`Users` (`votedUsers, userChoices, votes, points`) + نص «(+1 نقطة)» | **Verified** |
| B3 | عرض أسماء من صوّت | شاشة بـ «جاري تحميل الأسماء… / عضو غير معروف / (تصويت قديم)» | **Verified** |
| C1 | سجل حضور بالتاريخ + تفاصيل حضور كل عضو (تواريخ مسجلة) | `member_history`، «التواريخ المسجلة» | **Verified** |
| C2 | منع تسجيل نفس العضو مرتين في اليوم | «هذا العضو مسجل حضوره مسبقاً اليوم!» | **Verified** |
| C3 | إحصائيات: إجمالي الأعضاء، متوسط الحضور، آخر 10 بروفات | `analytics` + النصوص | **Verified** |
| C4 | إجراءات إدارية: تصفير نقاط عضو، تصفير غياب عضو، تصفير غياب الكورال كله، حذف عضو، تغيير كورال/اسم | نصوص التأكيد + `reset_points / reset_absence` | **Verified (لن تُنقل الحذفات الجماعية — انظر §6)** |
| C5 | حفظ الغياب لليوم مع تحذير تغييرات غير محفوظة | «لديك تغييرات غير محفوظة…» | **Verified** |
| D1 | لوحة المتصدرين + «الأوائل» + «لوحة الشرف للمنتظمين» | `leaderboard`, `Lij1` | **Verified** (معيار الانتظام: Unverified) |
| D2 | بطاقة QR كبيرة (كارنيه) ترفع السطوع | «اضغط على الكارنيه لتكبير الكود ورفع الإضاءة» | **Verified** |
| E1 | بروفة أسبوعية ثابتة (يوم + وقت) + مواعيد منفردة + نوع (بروفة/قداس/خدمة) | `isWeeklyRehearsal, dayOfWeek`, «اختر يوم البروفة الثابتة» | **Verified** |
| E2 | تذكيرين: قبل بـ 15 دقيقة وعند الموعد، قناة إشعارات «تنبيهات البروفات» | `RehearsalReminderReceiver`، نصوص «متبقي 15 دقيقة…» و«حان الآن موعد البروفة»، `SCHEDULE_EXACT_ALARM` | **Verified** |
| E3 | إعادة الجدولة عند إعادة تشغيل الجهاز | **لا يوجد** `BOOT_COMPLETED` receiver في المانيفست؛ تُعاد الجدولة فقط عند فتح التطبيق (مستمع Firestore يحفظ `rehearsal_reminder_ids`) | **Verified (غير موجود)** |
| E4 | خيار تفعيل/إيقاف التذكيرات للمستخدم | لم يظهر أي مفتاح مقابل | **غير موجود** |
| F1 | تحديث داخل التطبيق: المالك يرفع APK ويكتب `AppConfig/app_update`؛ المستخدم يرى «تحديث جديد متوفر» ويحمّل ويثبّت بـ PackageInstaller | `REQUEST_INSTALL_PACKAGES`، `smchoir_update_session`، `apkHash` | **Verified** |
| G1 | نموذج أدوار: Owner/Admin/Partner/Assistant/Leader/Editor/Member/Viewer + ترقية/تغيير رتبة + `canViewDetails` | `Users.role`، نصوص «ترقية أو تغيير رتبة» | **Verified (لن يُنقل — انظر §6)** |
| G2 | دخول بـ Google + username | `credentials-play-services-auth` | **خارج النطاق** |

## 3. New Features (غير موجودة في Abba Karas وستُضاف)
A1, A2, A3, A5 (ترانيم/مجلدات/مشغل/سلة) • B1–B3 (تصويت) • C1, C3 (سجل حضور تفصيلي + تحليلات) • D1 (الأوائل + انتظام) • E1 (بروفة أسبوعية ثابتة) • E2/E4 (تذكيرات 15د/عند الموعد + مفاتيح تفعيل) • F1 (إشعار تحديث) • تصفير نقاط عضو (كتسوية في السجل).

## 4. Overlapping Features (موجودة في الاثنين — يبقى نظام Abba Karas)
| الميزة | SM | Abba Karas | القرار |
|---|---|---|---|
| QR حضور + حضور يدوي + منع التكرار | ✔ | ✔ (معرّف المستند `eventId_memberId`) | نبقي AK؛ لا تغيير |
| نقاط الحضور | قيم ثابتة بحسب الوقت | قواعد قابلة للتعديل في الإعدادات | **نبقي AK بالكامل** |
| إضافة/خصم نقاط | ✔ | ✔ مع سبب وإشعار | نبقي AK |
| لوحة الترتيب | ✔ | ✔ بالنقاط | نوسّعها (الأوائل + الانتظام) |
| جدول المواعيد | `Schedules` | `events` | نوسّع `events` (لا collection جديدة للمواعيد) |
| كارنيه QR | ✔ | ✔ في الملف الشخصي | نضيف التكبير + رفع السطوع |

## 5. Unverified Features (لم يمكن تأكيد سلوكها — لم تُنقل كمؤكدة)
1. **قيم نقاط الحضور 13/10/8 والعقوبة 5**: ظهرت كثوابت (`13`, `8`, `10`, `5`) ومقارنة بنافذة 15 دقيقة، لكن شرط التفرع الكامل (control flow) لا يمكن استعادته بدون decompiler. لا حاجة لنقلها: نظام AK قابل للتعديل ومحتفظ به.
2. **معيار «الانتظام» في لوحة الشرف**: النص موجود، والحساب (نسبة؟ عدد؟) غير مؤكد. نُفّذ بنسبة الحضور الفعلية من سجلات AK (قرار تقني موثّق).
3. **نافذة تسجيل الحضور**: SM يستخدم `−30 دقيقة` إلى `+3 ساعات` (ثوابت 1,800,000 و10,800,000 ms)، AK يستخدم نافذته القابلة للتعديل — نبقي AK.
4. **سلوك استعادة ترنيمة مجلدها محذوف**: غير مؤكد؛ صُمّم بقرار تقني آمن (يُسأل المستخدم).
5. **صلاحيات كل رتبة** (من يستطيع ماذا بالضبط): غير قابلة للاستعادة بدقة.

## 6. قرارات تقنية وما لن يُنقل عمدًا
| البند | القرار | السبب |
|---|---|---|
| رفع MP3/صور عبر Cloudinary | **لا** (يعتمد على حساب Cloudinary للتطبيق الآخر `cloud name` ظاهر في الـ DEX — لن يُستخدم) | هذا الحساب ليس لنا |
| بديل رفع الصوت | Firebase Storage (نفس مشروع `youth-family-c039e`) **اختياري ويحتاج تفعيل يدوي**؛ والأساس رابط صوت مباشر | قيد الخطة/الإعداد |
| تنزيل وتثبيت APK تلقائيًا | **لا**. نعرض إشعار تحديث (إصدار + ملاحظات + رابط https + SHA-256 للتحقق) | طلبك: لا APK غير موثوقة؛ Capacitor بدون plugin تثبيت |
| 8 رتب (Owner…Viewer) | **لا**؛ نبقي `servant/member` | تغييرها يكسر الحسابات والقواعد القديمة |
| بريد المالك المكتوب في الكود (hardcoded owner) | **لا** | ثغرة تصميم؛ لن تُنقل |
| تصفير غياب الكورال/حذف عضو جماعي بلا رجعة | **لا** | يخالف «لا تحذف سجلات الحضور والنقاط». البديل: تصفير نقاط كتسوية مسجلة، وحذف المخدوم الفردي الموجود أصلًا |
| قيم نقاط SM | **لا** | AK قابل للتعديل |
| تسجيل الدخول بجوجل | **لا** | خارج النطاق |

## 7. Firebase Changes (إضافات فقط)
- **Collections جديدة:** `hymnFolders`, `hymns`, `polls`, `pollVotes`.
- **Documents جديدة داخل `config`:** `app_update`, `weekly` (قواعد `config` الحالية تكفي: قراءة للمسجلين وكتابة للخادم).
- **حقل اختياري جديد في `members`:** `lastVotePoll` (يمنع تكرار نقطة التصويت).
- **حقول اختيارية جديدة في `events`:** `weekly`, `series` (يتجاهلها الكود القديم).
- **Rules:** إضافة فقط (`firestore.rules`) + فرع جديد في تحديث `members` لنقطة التصويت؛ لا تغيير لأي قاعدة قائمة.
- **Storage:** ملف `storage.rules` جديد (اختياري، لا يُنشر تلقائيًا).
- **لا نشر تلقائي، لا حذف، لا تعديل بيانات إنتاج.**

## 8. Risks
| الخطر | التخفيف |
|---|---|
| القواعد الجديدة غير منشورة → الشاشات الجديدة تفشل بصلاحيات | الشاشات القديمة لا تعتمد عليها؛ مستمعات الـ collections الجديدة معزولة (`console.warn` فقط) ورسالة واضحة في الشاشة الجديدة |
| لا يمكن اختبار القواعد بدون Firebase Emulator (غير متاح هنا) | موثّق في `TEST_REPORT.md` كـ «يتطلب اختبار يدوي» |
| Firebase Storage قد يتطلب خطة Blaze | الرفع اختياري؛ رسالة خطأ واضحة؛ الرابط المباشر يعمل دائمًا |
| إشعارات محلية على Windows | بديل داخل التطبيق عبر Notification API أثناء تشغيل التطبيق |
| روابط Drive/Dropbox قد تتغير سياساتها | تحويل تلقائي + رسالة خطأ تشغيل واضحة |
