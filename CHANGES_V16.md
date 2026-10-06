# v16 = دمج lis_merged_v15 + lis_merged_v10_updated

الأساس: v15 (نظام الأساليب الأربعة + النتائج السابقة لكل زيارة + التقرير الشامل + الطباعة التلقائية لأي تحليل بلا تصميم).
اللي انضاف من v10_updated:
1. ملاحظة الباراميتر بتقارير الفحص (exam_report_shared.html): عنوان اختياري + زر إظهار/إخفاء منفصل عن الكتابة.
   database.py: أعمدة results.note_label / note_visible. app.py: مسار param-note يحفظ العنوان + مسار param-note-visibility الجديد + param_notes صار dict.
2. صفحة "زيارة جديدة": سطر "🔁 نفس التحليل تكرر N مرات بتاريخ ..." رجع تحت كل تحليل قابل للدمج (API يرجّع prior_count/prior_dates).
اللي ما انأخذ من v10 لأن v15 يغطيه بشكل أشمل:
- ensure_fbs_report_template + إنشاء قالب عند تحليل جديد → استبدلتها _auto_report_template (v15) اللي تشتغل لأي تحليل بلا تصميم، فيطلع TSH / VitD3 / A1c مثل FBS.
- previous_results_count بالإعدادات → v15 فيها عدد/ترتيب النتائج السابقة بمصمم التقارير + اختيار لكل زيارة.
- previous_list / note_info بـ custom_v2 و combined_panel → استبدلها قالب result_styles.html + report_row_notes.
تحقق: py_compile لـ app/database/accounts_search ✔، تشغيل Flask فعلي بقاعدة جديدة: طباعة A1c/TSH/VitD3/FBS/HBsAg بدون قالب محفوظ (200)، اللوحة المجمّعة، معاينة المصمم للأساليب الأربعة.
لم يُختبر: ملفات .bat/.vbs، وlicense_manager/auto_updater/barcode_gen (غير موجودة بالزيبين، استُبدلت بنسخ وهمية بالاختبار فقط).
