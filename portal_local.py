# -*- coding: utf-8 -*-
"""
portal_local.py — بوابة نتائج المريض المدمجة داخل برنامج المختبر (بدون Render ولا GitHub)
=========================================================================================
سيرفر صغير منفصل (منفذ 9091، على 127.0.0.1 فقط) يعرض فقط:
    /r/<رمز>        صفحة النتائج للمريض (جدول + أزرار PDF)
    /r/<رمز>/pdf    ملف PDF
    /healthz        فحص
ولا شي غيرهم: لا تسجيل دخول، لا إعدادات، لا مرضى، لا أي مسار من برنامج المختبر نفسه.
هذا السيرفر الوحيد الذي يُعرَّض للإنترنت (عبر Tailscale Funnel أو Cloudflare Tunnel) —
برنامج المختبر الرئيسي (منفذ 9090) يبقى داخل شبكتك فقط.

الكتابة تتم من داخل نفس العملية (cloud_sync → store/delete) وليس عبر HTTP، فلا يوجد مفتاح سري
ولا مسار كتابة معرّض للإنترنت أصلاً. البيانات بملف portal_public.db بجانب lis.db.
"""
import os
import re
import sqlite3
import threading
from datetime import datetime, timedelta
from urllib.parse import quote

from flask import Flask, Response, abort, render_template, request

import database

PORT = int(os.environ.get("LIS_PORTAL_PORT", "9091"))
DB_FILE = os.path.join(database._BASE_DIR, "portal_public.db")
TZ_OFFSET_HOURS = float(os.environ.get("TZ_OFFSET_HOURS", "3"))   # العراق
TOKEN_RE = re.compile(r"^[A-Za-z0-9_\-]{20,80}$")

# static_folder=None ضروري جدًا: بدونه Flask يفتح /static/... تلقائيًا فيتعرّض مجلد static كله (أختام الدكاترة،
# وملفات PDF المرضى بـ static/whatsapp_pdfs) على الإنترنت. هذا السيرفر ما يقدّم أي ملف ثابت أبدًا.
app = Flask(__name__, static_folder=None,
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "portal_templates"))
_lock = threading.Lock()
_started = False


def _db():
    conn = sqlite3.connect(DB_FILE, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    with _lock:
        conn = _db()
        conn.execute("""CREATE TABLE IF NOT EXISTS reports (
            token TEXT PRIMARY KEY, patient_name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
            eta_text TEXT, results_html TEXT, pdf BLOB, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(reports)")}
        if "lab_name" not in cols:
            conn.execute("ALTER TABLE reports ADD COLUMN lab_name TEXT")
        conn.commit()
        conn.close()


def _default_lab_name():
    try:
        db = database.get_db()
        try:
            return (database.get_setting(db, "app_name_ar", "") or database.get_setting(db, "app_name", "")
                    or "مختبر التحاليل الطبية")[:120]
        finally:
            db.close()
    except Exception:  # noqa: BLE001
        return "مختبر التحاليل الطبية"


def retention_days():
    try:
        db = database.get_db()
        try:
            return max(1, min(365, int(float(database.get_setting(db, "portal_retention_days", "30") or 30))))
        finally:
            db.close()
    except Exception:  # noqa: BLE001
        return 30


# ------------------------------------------------------------------ الكتابة (داخل العملية فقط)
def store(token, patient_name, status, eta_text=None, results_html=None, pdf_bytes=None, lab_name=None):
    now = datetime.utcnow().isoformat()
    with _lock:
        conn = _db()
        try:
            if conn.execute("SELECT 1 FROM reports WHERE token=?", (token,)).fetchone():
                conn.execute("UPDATE reports SET patient_name=?, lab_name=?, status=?, eta_text=?, results_html=?, pdf=?, updated_at=? WHERE token=?",
                             (patient_name, lab_name, status, eta_text, results_html, pdf_bytes, now, token))
            else:
                conn.execute("INSERT INTO reports (token, patient_name, lab_name, status, eta_text, results_html, pdf, created_at, updated_at) "
                             "VALUES (?,?,?,?,?,?,?,?,?)", (token, patient_name, lab_name, status, eta_text, results_html, pdf_bytes, now, now))
            conn.commit()
        finally:
            conn.close()


def delete(token):
    with _lock:
        conn = _db()
        conn.execute("DELETE FROM reports WHERE token=?", (token,))
        conn.commit()
        conn.close()


def purge_old():
    cutoff = (datetime.utcnow() - timedelta(days=retention_days())).isoformat()
    with _lock:
        conn = _db()
        n = conn.execute("DELETE FROM reports WHERE created_at < ?", (cutoff,)).rowcount
        conn.commit()
        conn.close()
    return n


# ------------------------------------------------------------------ القراءة (العامة)
def _local(iso, fmt):
    try:
        return (datetime.fromisoformat(iso) + timedelta(hours=TZ_OFFSET_HOURS)).strftime(fmt)
    except (TypeError, ValueError):
        return iso or ""


def _pdf_filename(name, stamp):
    safe = re.sub(r"[^\w\- ]+", "", name or "", flags=re.UNICODE).strip().replace(" ", "_")[:40] or "patient"
    return f"نتائج-{safe}-{_local(stamp, '%Y-%m-%d')}.pdf"


@app.after_request
def _headers(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.route("/healthz")
def healthz():
    return "lis-portal-ok", 200


@app.route("/")
def home():
    return "Lab Results Portal — OK", 200


@app.route("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /\n", 200, {"Content-Type": "text/plain"}


@app.route("/r/<token>")
def view_result(token):
    if not TOKEN_RE.match(token):
        abort(404)
    purge_old()
    conn = _db()
    row = conn.execute("SELECT token, patient_name, lab_name, status, eta_text, results_html, created_at, updated_at, "
                       "(pdf IS NOT NULL) AS has_pdf FROM reports WHERE token=?", (token,)).fetchone()
    conn.close()
    if not row:
        abort(404)
    days = retention_days()
    try:
        exp = (datetime.fromisoformat(row["created_at"]) + timedelta(days=days, hours=TZ_OFFSET_HOURS)).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        exp = ""
    return render_template(
        "result_page.html", patient_name=row["patient_name"], lab_name=(row["lab_name"] or _default_lab_name()),
        status=row["status"], eta_text=row["eta_text"] or "",
        results_html=row["results_html"] or "", updated_at=_local(row["updated_at"], "%Y-%m-%d %H:%M"),
        has_pdf=bool(row["has_pdf"]) and row["status"] == "ready", pdf_url=f"/r/{token}/pdf",
        pdf_filename=_pdf_filename(row["patient_name"], row["updated_at"]), expires_on=exp, retention_days=days)


@app.route("/r/<token>/pdf")
def download_pdf(token):
    if not TOKEN_RE.match(token):
        abort(404)
    conn = _db()
    row = conn.execute("SELECT patient_name, status, updated_at, pdf FROM reports WHERE token=?", (token,)).fetchone()
    conn.close()
    if not row or row["status"] != "ready" or row["pdf"] is None:
        abort(404)
    disp = "inline" if request.args.get("view") == "1" else "attachment"
    resp = Response(bytes(row["pdf"]), mimetype="application/pdf")
    resp.headers["Content-Disposition"] = (
        f"{disp}; filename=\"results.pdf\"; filename*=UTF-8''{quote(_pdf_filename(row['patient_name'], row['updated_at']))}")
    resp.headers["Content-Length"] = str(len(row["pdf"]))
    return resp


@app.errorhandler(404)
def not_found(e):
    return render_template("result_page.html", not_found=True, lab_name=_default_lab_name()), 404


# ------------------------------------------------------------------ التشغيل
def start_server():
    """يشغّل البوابة بخيط خلفي على 127.0.0.1:9091 (محلي فقط — النفق هو اللي يعرّضه للإنترنت)."""
    global _started
    if _started:
        return
    _started = True
    init()

    def _run():
        try:
            from werkzeug.serving import make_server
            make_server("127.0.0.1", PORT, app, threaded=True).serve_forever()
        except OSError:
            pass   # المنفذ مشغول (نسخة ثانية شغالة)
    threading.Thread(target=_run, name="portal-public", daemon=True).start()
