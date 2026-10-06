# v23 = v22 + تجهيز العملاء + اسم المختبر ديناميكي + كاش PDF
- البوابة (cloud_portal): اسم المختبر يجي من البرنامج (lab_name) أو متغير LAB_NAME بدل النص الثابت.
- cloud_sync.py: يرسل lab_name (من app_name_ar/app_name)، كاش PDF على القرص، وإيقاف إعادة التوليد الدورية كل 6 ساعات
  للنتائج الجاهزة (كانت تعيد توليد كل PDFات آخر 31 يوم — عيب بنسخة v21/v22 أصلحته).
- database.py: apply_client_preset — portal_preset.json يُطبَّق مرة وحدة عند أول تشغيل.
- tools/make_client_package.py: يطلع زيب جاهز للعميل بدون بيانات مختبرك.
- دليل_تجهيز_عميل_جديد.txt.
اختبار: دفع PDF أول مرة (1 توليد) ثم لا توليد؛ مسح قاعدة البوابة ثم استعادة بـ0 توليد من الكاش؛ الزيب الناتج بلا lis.db/شعار/PDFات/tools؛
تثبيت نظيف من الزيب يطبّق الإعدادات مرة وحدة ولا يطغى على تعديل العميل.
لم يُختبر: Render الفعلي بخدمتين، Public Git Repository، ويندوز.

## تحديث v24 (إصلاح التشغيل)
- lis_server.bat / open_lab.bat / lis_server_hidden.vbs: نسخة إصلاحك (ASCII فقط + CRLF + PYTHONUTF8) — النسخ القديمة بالزيبات السابقة كانت LF مع حروف عربية داخل ملفات .bat وهذا سبب أن الاختصار لا يشغّل السيرفر.
- install_autostart.bat / uninstall_autostart.bat: نفس العلة، أعيدت كتابتها ASCII + CRLF (المنطق نفسه).
- .gitattributes: يفرض CRLF على bat/cmd/vbs عند Git حتى لا تتحول لـLF مرة ثانية.

## v25: نسخة العميل بنقرة وحدة
- tools/seal_client_package.py: ينظّف قاعدة العميل (يمسح المرضى/الزيارات/النتائج/الفواتير/السجلات والترخيص والمفاتيح/مسارات جهازك)، يبقي الإعدادات والتحاليل والنسب والتصاميم والأختام، يجمّع زيب فيه INSTALL.bat وrequirements.txt.
- INSTALL.bat (يتولّد داخل الزيب): ينسخ لـC:\LIS، يحدد/يثبّت Python، يبني venv، pip install، playwright chromium، اختصارات، تشغيل.
- دليل_تجهيز_عميل_جديد.txt أعيد كتابته.
