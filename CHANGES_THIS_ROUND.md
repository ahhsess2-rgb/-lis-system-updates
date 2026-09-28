# تعديلات هذي الجولة (فوق زيب merged_final)

1. إصلاح خطأ سببته أنا سابقًا: التقرير اليومي كان يقرأ v.referring_doctor_name من جدول visits
   وهذا العمود غير موجود (موجود فقط بجدول saved_reports) → كان سيعطي خطأ SQL. صار الطبيب
   المرسل يُقرأ من visits.doctor_id عبر جدول doctors. (app.py: daily_report)
2. مصمم التقارير: بُني الباك-إند من الصفر (كان غير موجود بزيبك) + الواجهة:
   - database.py: أعمدة test_definitions: show_lab_stamp, show_doctor_stamp (الافتراضي 1 = السلوك القديم),
     hide_signature_box, signature_position. و test_parameters: report_column.
   - app.py: mode جديد print_options بمصمم التقارير + تطبيقها بالطباعة (تصفية الأختام التلقائية،
     إخفاء صندوق التوقيع، موضعه).
   - templates/reports/base_report.html: قراءة hide_signature_box/signature_position.
   - templates/management/report_designer.html: نموذج "خيارات الختم والتوقيع" + عمود كل باراميتر.
3. accounts_search.html: مربع كتابة اسم التحليل لتصفية قائمة التحاليل.
ملاحظة: report_column يُحفظ من المصمم لكن ما انربط بعد بتخطيط أي قالب طباعة.

4. إصلاح خطأ قديم مؤكد من error_log.txt عندك: base_report.html كان يستدعي
   "partials/stamp_picker.html" بينما الملف بمسار reports/partials/stamp_picker.html
   → أي تقرير مفعّل له صندوق الختم كان يعطي TemplateNotFound. صار المسار الصحيح.
   تحققت بتشغيل طباعة Blood Film: خيارات الختم/صندوق التوقيع/موضعه تنعكس فعليًا بالطباعة.

5. دمج الزيبين الجديدين (lis_updates + files):
   - app.py و templates: من lis_updates (يحتوي كل تعديلاتي السابقة + ميزات جديدة: مظهر الشاشة الرئيسية
     لكل واجهة، أرشفة PDF عند الحفظ، زر الطباعة+الحفظ عبر /reports/print-and-save، إخفاء القائمة الجانبية).
     زر الطباعة هسه يعتمد على نسخة lis_updates (أحدث من نسختي، حفظ بدون إعادة تحميل).
   - app.py رجعت debug=False (كان True بنسخة lis_updates: خطر أمني على الشبكة + يشغّل الخيوط الخلفية مرتين).
   - التشغيل التلقائي من files.zip: install_autostart.bat (مرة وحدة) + lis_server.bat (حارس يعيد التشغيل)
     + lis_server_hidden.vbs + open_lab.bat + uninstall_autostart.bat.
     أضفت تدوير server_log.txt (فوق 5MB). حذفت start_lab.bat/start_lab_hidden.vbs القديمين (استبدلتهم).
   - اختبار (سيرفر Flask حقيقي عندي بقاعدة جديدة): dashboard، dashboard-look، التقرير اليومي والشهري،
     بحث المختبر والإحالة، الأختام، مصمم التقارير، طباعة Blood Film، وpint-and-save: كلها 200 بدون أخطاء.
     ملفات .bat/.vbs ما اختبرتها (ما عندي ويندوز).

6. دمج modified_files_only.zip:
   - جديد: astm_host.py، templates/interface_choose.html، templates/master/host_interface.html (خيار الإرسال التلقائي للاستقبال).
   - app.py: أضفت فقط تعديلات host_auto_send_to_reception (3 مواضع) فوق نسخة lis_updates (نسخة الملف الجديد كانت أقدم من lis_updates، ما فيها أرشفة PDF ولا مظهر الشاشة ولا الطباعة+الحفظ الجديدة، فما استبدلتها).
   - settings.html: من الملف الجديد (حقول حجم صورة شاشة الترحيب).
   - dashboard.html: أبقيت نسخة lis_updates (أحدث: طبقة اللون والسطوع).
   - أضفت templates/designer/layout.html (القالب اللي يمدّده host_interface.html) وتأكدت إن صفحة ربط الأجهزة تشتغل معه (200).
