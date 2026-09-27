# -*- coding: utf-8 -*-
"""
accounts_search.py
=============================================================================
منطق البحث الموحّد لصفحات الحسابات (يومي/شهري/ربع سنوي/نصف سنوي/سنوي) —
زر "🔍 بحث وتصدير" الجديد. ملف مستقل حتى لا يتضخم app.py أكثر، ويُستورد
منه مباشرة:

    import accounts_search as acs

يغطي وضعين:
  1) البحث العادي (basic): عدد التحاليل + أسماء المرضى، بفلترة تحليل واحد/
     عدة تحاليل/الكل، وتاريخ واحد أو فترة.
  2) بحث الطبيب الفاحص (doctor): كل التحاليل التي يتقاضى عنها هذا الطبيب
     أجرًا (examining_doctor_rates) خلال فترة، مجمّعة شهريًا ثم إجمالي
     الفترة، مع اسم كل مريض وسعر (أجر) كل تحليل والمجموع الكلي.

مصدر "السعر" ببحث الطبيب الفاحص هو *أجر الطبيب* (examining_doctor_rates.rate)
لا سعر التحليل على المريض — لأن هذا تقرير "كم يستحق هذا الطبيب"، بنفس
المنطق المستخدم أصلاً بحساب visits.examining_doctor_fee بباقي البرنامج
(راجع compute_examining_doctor_fee بـdatabase.py). أي تحليل fee_waived=1
يُستثنى من كل مجاميع السعر/الأجر بكلا الوضعين (نفس قاعدة period_breakdown
الموجودة أصلاً بـapp.py)، لكن لا يُستثنى من "عدد التحاليل" بوضع البحث
العادي (لأنه تحليل تم فعليًا، فقط بدون أجر/سعر).

كل التواريخ الداخلة/الخارجة بهذا الملف بصيغة ISO (YYYY-MM-DD) — التحويل
لعرض DD/MM/YYYY يصير بالقالب (Jinja) وقت العرض فقط عبر فلتر `ddmmyyyy`
(انظر تسجيله بـapp.py بالأسفل).
"""
from datetime import date, timedelta
import calendar


# ---------------------------------------------------------------- تواريخ --
def ddmmyyyy(value):
    """فلتر Jinja: '2026-09-12' -> '12/09/2026'. يتجاهل بصمت أي قيمة غير
    متوقعة (فاضي، None، أو نص مو تاريخ) ويرجعها كما هي بدل ما يفشل الصفحة."""
    if not value:
        return ""
    try:
        y, m, d = str(value)[:10].split("-")
        return f"{d}/{m}/{y}"
    except (ValueError, AttributeError):
        return value


def quarter_bounds(year, quarter):
    """(start_month, end_month) للربع 1..4."""
    quarter = max(1, min(4, int(quarter)))
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    return start_month, end_month


def resolve_date_range(args):
    """يبني (date_from, date_to) بصيغة ISO من query params الموحّدة
    المستخدمة بكل نماذج البحث بهذا الملف:
      - date_mode=single  &date=YYYY-MM-DD
      - date_mode=range   &date_from=...&date_to=...
    افتراضيًا (لا شي مُرسَل): اليوم الحالي فقط، حتى ما تنكسر الصفحة لو
    فُتحت بدون أي معامل."""
    mode = args.get("date_mode", "single")
    today = date.today().isoformat()
    if mode == "range":
        d_from = args.get("date_from") or today
        d_to = args.get("date_to") or today
    else:
        d_from = d_to = args.get("date") or today
    if d_from > d_to:
        d_from, d_to = d_to, d_from
    return d_from, d_to


# ---------------------------------------------------------------- عام -----
def get_test_choices(db):
    """(id, name) لكل تحاليل الكتالوج الفعّالة — لملء قائمة اختيار
    التحاليل المتعددة بشاشة البحث."""
    rows = db.execute(
        "SELECT id, name FROM test_definitions WHERE is_active=1 ORDER BY name"
    ).fetchall()
    return [(r["id"], r["name"]) for r in rows]


def _test_filter_sql(test_ids):
    """يرجّع (شرط SQL جاهز للّصق بعد AND، أو '1=1' لو 'الكل', قيم الربط)."""
    if not test_ids:
        return "1=1", []
    placeholders = ",".join("?" for _ in test_ids)
    return f"td.id IN ({placeholders})", list(test_ids)


# ---------------------------------------------------------------- البحث العادي --
def run_basic_search(db, date_from, date_to, test_ids, mode):
    """mode: 'counts' أو 'names'.

    counts  -> {"rows": [{"test_name","date","count"}...], "total_count": N}
               مرتبة الأحدث فالأقدم، تحليل داخل كل تاريخ.
    names   -> {"rows": [{"patient_name","test_name","date","price"}...],
                "total_price": مجموع الأسعار (fee_waived مُستثنى)}
               مرتبة تنازليًا حسب التاريخ.
    """
    test_where, test_params = _test_filter_sql(test_ids)

    if mode == "counts":
        rows = db.execute(
            f"""
            SELECT substr(v.created_at,1,10) as day, td.name as test_name,
                   COUNT(*) as cnt
            FROM order_tests ot
            JOIN orders o ON o.id = ot.order_id
            JOIN visits v ON v.id = o.visit_id
            JOIN test_definitions td ON td.id = ot.test_definition_id
            WHERE substr(v.created_at,1,10) BETWEEN ? AND ?
              AND {test_where}
            GROUP BY day, td.id
            ORDER BY day DESC, td.name
            """,
            [date_from, date_to] + test_params,
        ).fetchall()
        out_rows = [{"test_name": r["test_name"], "date": r["day"], "count": r["cnt"]} for r in rows]
        return {"rows": out_rows, "total_count": sum(r["count"] for r in out_rows)}

    # mode == "names"
    rows = db.execute(
        f"""
        SELECT p.full_name as patient_name, p.id as patient_id,
               p.age as age, p.age_unit as age_unit, p.gender as gender,
               v.registration_number as reg_no,
               td.name as test_name, substr(v.created_at,1,10) as day,
               COALESCE(ot.price, td.price) as price, ot.fee_waived as fee_waived
        FROM order_tests ot
        JOIN orders o ON o.id = ot.order_id
        JOIN visits v ON v.id = o.visit_id
        JOIN patients p ON p.id = v.patient_id
        JOIN test_definitions td ON td.id = ot.test_definition_id
        WHERE substr(v.created_at,1,10) BETWEEN ? AND ?
          AND {test_where}
        ORDER BY v.created_at DESC, p.full_name
        """,
        [date_from, date_to] + test_params,
    ).fetchall()
    out_rows = []
    total_price = 0.0
    for r in rows:
        price = r["price"] or 0
        if not r["fee_waived"]:
            total_price += price
        out_rows.append({
            "patient_name": r["patient_name"], "patient_id": r["patient_id"],
            "age": r["age"], "age_unit": r["age_unit"], "gender": r["gender"],
            "reg_no": r["reg_no"], "test_name": r["test_name"], "date": r["day"],
            "price": price, "fee_waived": bool(r["fee_waived"]),
        })
    return {"rows": out_rows, "total_price": total_price}


# ---------------------------------------------------------------- بحث الطبيب الفاحص --
def run_doctor_search(db, doctor_name, date_from, date_to, test_ids):
    """يرجّع dict فيها:
      by_test_month: [{"test_name","month" (YYYY-MM), "count"}...] مرتبة
                      test_name ثم month (للجدول "Blood film = 30 بشهر
                      أيلول" المطلوب).
      by_test_total: [{"test_name","count","rate","subtotal"}...] إجمالي
                      الفترة كاملة لكل تحليل (rate هو أجر التحليل الواحد
                      لهذا الطبيب — إذا اختلف الأجر تاريخيًا لنفس التحليل
                      هذا احتمال نظري فقط، rate هنا هو المسجَّل حاليًا).
      patient_rows: [{"patient_name","test_name","date","rate"}...] —
                    التفصيل الكامل مريض-مريض، تنازلي بالتاريخ (يُستخدم
                    بالتصدير التفصيلي وبعرض الشاشة).
      total: المجموع الكلي لأجر الطبيب بكامل الفترة (fee_waived مُستثنى).
      doctor_name/date_from/date_to: تمريرها بالإرجاع فقط لسهولة الطباعة.

    "بدون تحديد تحاليل" (test_ids فاضية) = تلقائيًا كل تحليل عنده أجر
    مسجَّل لهذا الطبيب بجدول examining_doctor_rates (نفس المصدر اللي
    يعتمد عليه احتساب visits.examining_doctor_fee أصلاً بباقي البرنامج) —
    هذا هو "بدون الحاجة لتحديدها" المطلوب.
    """
    test_where, test_params = _test_filter_sql(test_ids)
    rows = db.execute(
        f"""
        SELECT p.full_name as patient_name, td.id as test_id, td.name as test_name,
               substr(v.created_at,1,10) as day, edr.rate as rate, ot.fee_waived as fee_waived
        FROM order_tests ot
        JOIN orders o ON o.id = ot.order_id
        JOIN visits v ON v.id = o.visit_id
        JOIN patients p ON p.id = v.patient_id
        JOIN test_definitions td ON td.id = ot.test_definition_id
        JOIN examining_doctor_rates edr
             ON edr.doctor_name = v.examining_doctor AND edr.test_definition_id = td.id
        WHERE v.examining_doctor = ?
          AND substr(v.created_at,1,10) BETWEEN ? AND ?
          AND {test_where}
        ORDER BY v.created_at DESC, td.name
        """,
        [doctor_name, date_from, date_to] + test_params,
    ).fetchall()

    by_test_month = {}   # (test_name, month) -> count
    by_test_total = {}   # test_name -> {"count","rate","subtotal"}
    patient_rows = []
    total = 0.0
    for r in rows:
        billable = not r["fee_waived"]
        rate = r["rate"] or 0
        month = r["day"][:7]
        key_m = (r["test_name"], month)
        by_test_month[key_m] = by_test_month.get(key_m, 0) + 1
        t = by_test_total.setdefault(r["test_name"], {"test_name": r["test_name"], "count": 0,
                                                        "rate": rate, "subtotal": 0.0})
        t["count"] += 1
        if billable:
            t["subtotal"] += rate
            total += rate
        patient_rows.append({
            "patient_name": r["patient_name"], "test_name": r["test_name"],
            "date": r["day"], "rate": rate, "fee_waived": r["fee_waived"],
        })

    by_test_month_rows = [
        {"test_name": k[0], "month": k[1], "count": v}
        for k, v in sorted(by_test_month.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    ]
    by_test_total_rows = sorted(by_test_total.values(), key=lambda x: x["test_name"])

    return {
        "doctor_name": doctor_name, "date_from": date_from, "date_to": date_to,
        "by_test_month": by_test_month_rows, "by_test_total": by_test_total_rows,
        "patient_rows": patient_rows, "total": total,
    }


def get_examining_doctor_names(db):
    """أسماء الأطباء الفاحصين لملء قائمة اختيار الطبيب بشاشة البحث —
    نفس examining_doctors_list المستخدمة بباقي البرنامج."""
    rows = db.execute("SELECT name FROM examining_doctors_list ORDER BY sort_order, id").fetchall()
    return [r["name"] for r in rows]
