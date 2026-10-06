# v21 = v20 + PDF للمريض + استعادة تلقائية للبوابة
- cloud_sync.py: set_pdf_maker، إرفاق pdf_b64 عند status=ready، /api/missing كل 5 دقائق، عرض النسب المتعددة بأسطر مستقلة (LTR).
- app.py: _portal_make_pdf + إعداد portal_pdf_enabled.
- settings.html: خانة إرفاق PDF.
اختبار: بوابة Flask محلية + برنامج المختبر الكامل بقاعدة فيها A1c/TSH/VitD3/FBS/HBsAg:
دفع النتيجة مع PDF (5 صفحات، 245KB) ✔، تنزيل بالاسم العربي ✔، زر المشاركة (محاكاة navigator.share) ✔،
حذف قاعدة البوابة ثم استعادة تلقائية ✔، printed_at لم يتغير ✔.
لم يُختبر: pdf_export الحقيقي عندك (استعملت بديلاً Chromium)، Render الفعلي، مشاركة الملفات على آيفون/أندرويد حقيقيين.
