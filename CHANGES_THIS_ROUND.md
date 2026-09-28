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
