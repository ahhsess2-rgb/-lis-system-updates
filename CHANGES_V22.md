# v22 = v21 + بوابة مدمجة (بدون Render/GitHub)
- جديد portal_local.py: سيرفر عام صغير (127.0.0.1:9091) يعرض /r/<token> و /r/<token>/pdf و /healthz فقط.
  static_folder=None (بدونه كان /static/... ينكشف: أختام + PDFات واتساب) — اكتشفته بفحص الأمان وسددته.
- cloud_sync.py: mode=local|remote، تسليم داخل العملية (بدون مفتاح سري ولا HTTP)، اختبار الاتصال يفحص الرابط العام (يشترط https)،
  إلغاء الرمز يحذف محليًا، فشل PDF يُسجَّل بـ portal_state.last_error.
- app.py/settings.html: اختيار الطريقة، مدة البقاء، تعليمات Tailscale داخل بطاقة الإعدادات.
- pdf_export.py الحقيقي (المرفوع) + static/whatsapp_pdfs.
اختبار بالبرنامج الكامل + pdf_export الحقيقي: pending→ready، PDF 5 صفحات، تنزيل/مشاركة بموبايل محاكى،
المنفذ العام 127.0.0.1 فقط، مسارات المختبر (/login, /management, /api, /static, /lis.db) كلها 404، البيانات تبقى بعد إعادة التشغيل، printed_at ما تغيّر.
لم يُختبر: Tailscale الحقيقي، موبايل حقيقي، barcode_gen الحقيقي (QR)، Windows.
