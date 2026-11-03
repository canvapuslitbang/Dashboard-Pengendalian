# -*- coding: utf-8 -*-
"""Dashboard Pengendalian & Pengambilan Keputusan SATRIA Puslitbang Polri.

Aplikasi Resmi Tata Kelola Keuangan & Kinerja Berbasis Risiko:
- Peran Tunggal SUPER ADMIN (Akses Penuh Seluruh Sistem & Manajemen Akun/Subline).
- Sistem MULTI-ADMIN dengan isolasi data terpisah berdasarkan Subline/Unit Kerja.
- Desain visual Modern Government Dashboard dengan identitas resmi Mako Puslitbang Polri.
- Seluruh fitur lama (Anggaran, Kontrak, Risiko, Milestone, Keputusan, Impor SAKTI/OM-SPAN) 100% terjaga.
"""

from datetime import date, datetime
import base64
import os
import pandas as pd
import streamlit as st

import db
import impor

_HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(_HERE, "assets")
_IKON = os.path.join(ASSET, "satria_favicon.png")

st.set_page_config(
    page_title="SATRIA Puslitbang Polri — Dashboard Pengendalian & Keputusan",
    page_icon=(_IKON if os.path.exists(_IKON) else "📊"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inisialisasi dan migrasi database
db.init()

# ----------------------------------------------------------- direktori dokumen & aset ----
PILAR_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "2. LPP PKN II TH 2026", "3 Pilar Output SATRIA"
)
DOKUMEN_PILAR = [
    "04. Matriks Alur Proses dan Deadline - SATRIA Puslitbang.docx",
    "01. SOP Percepatan Pengadaan Pra-DIPA dan Mitigasi Transisi KPA - SATRIA Puslitbang.docx",
    "02. Risk Register Kinerja - SATRIA Puslitbang.docx",
    "03. Kartu Kendali Bulanan KPA Berbasis Risiko - SATRIA Puslitbang.docx",
]


def _aset(nama):
    """Membaca berkas aset sebagai bytes (aman jika berkas tidak ditemukan)."""
    try:
        with open(os.path.join(ASSET, nama), "rb") as f:
            return f.read()
    except OSError:
        return None


def _data_uri(nama):
    b = _aset(nama)
    if not b:
        return None
    ext = os.path.splitext(nama)[1].lower()
    if ext in (".jpg", ".jpeg"):
        mime = "image/jpeg"
    elif ext == ".webp":
        mime = "image/webp"
    elif ext == ".gif":
        mime = "image/gif"
    else:
        mime = "image/png"
    return "data:%s;base64,%s" % (mime, base64.b64encode(b).decode())


# ----------------------------------------------------------- tema visual modern ----
def tema():
    """Gaya tampilan Modern Government Dashboard & Enterprise Administration."""
    # Foto Mako Puslitbang Polri Terbaru sebagai latar hero dan identitas instansi
    foto_mako = _data_uri("MAKO PUSLITBANG TERBARU.jpeg") or _data_uri("gedung_band.jpg") or ""
    css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --gov-navy-900: #071527;
        --gov-navy-800: #0d2342;
        --gov-navy-700: #143564;
        --gov-navy-600: #1d4b8f;
        --gov-gold-500: #c99726;
        --gov-gold-400: #e5b33d;
        --gov-gold-300: #f7d67e;
        --gov-slate-50: #f8fafc;
        --gov-slate-100: #f1f5f9;
        --gov-slate-200: #e2e8f0;
        --gov-slate-500: #64748b;
        --gov-slate-700: #334155;
        --gov-slate-900: #0f172a;
        --gov-emerald: #059669;
        --gov-crimson: #dc2626;
        --gov-amber: #d97706;
    }

    html, body, [data-testid="stAppViewContainer"] * {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    [data-testid='stAppViewContainer'] {
        background:
            radial-gradient(1200px 500px at 100% -5%, rgba(20, 53, 100, 0.12), transparent 60%),
            radial-gradient(900px 450px at -5% 5%, rgba(201, 151, 38, 0.10), transparent 55%),
            linear-gradient(180deg, #f8fafc 0%, #f1f5f9 60%, #eef3fb 100%);
        background-attachment: fixed;
    }

    [data-testid='stHeader'] { background: transparent; }

    /* ================================================================
       SIDEBAR PREMIUM — Modern Government Enterprise Design
       SATRIA Puslitbang Polri | Deep Navy + Gold Accent Theme
    ================================================================ */

    /* ---- Base Sidebar Container ---- */
    [data-testid='stSidebar'] {
        background: linear-gradient(180deg,
            #040e1c 0%,
            #071527 18%,
            #0a1e35 42%,
            #0d2342 72%,
            #102a4f 100%);
        border-right: 1px solid rgba(201, 151, 38, 0.18);
        box-shadow: 6px 0 32px rgba(4, 14, 28, 0.55);
        min-width: 0;
    }
    [data-testid='stSidebar'] > div { padding-top: 0 !important; }
    [data-testid='stSidebar'] * { color: #e2e8f0 !important; }
    [data-testid='stSidebar'] hr {
        border: none !important;
        border-top: 1px solid rgba(201, 151, 38, 0.15) !important;
        margin: 6px 0 !important;
    }

    /* ---- Sidebar Scrollbar ---- */
    [data-testid='stSidebar'] ::-webkit-scrollbar { width: 3px; }
    [data-testid='stSidebar'] ::-webkit-scrollbar-thumb {
        background: rgba(201,151,38,0.35); border-radius: 999px;
    }
    [data-testid='stSidebar'] ::-webkit-scrollbar-track { background: transparent; }

    /* ================================================================
       BRANDING HEADER
    ================================================================ */
    .sb-brand-wrap {
        position: relative;
        padding: 18px 16px 14px;
        border-bottom: 1px solid rgba(201, 151, 38, 0.12);
        margin-bottom: 4px;
    }
    .sb-brand-inner { display: flex; align-items: center; gap: 11px; }
    .sb-logo-box {
        flex: 0 0 auto;
        width: 46px; height: 46px;
        border-radius: 12px;
        background: rgba(255,255,255,0.95);
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35), 0 0 0 1px rgba(201,151,38,0.3);
    }
    .sb-logo-box img { width: 36px; height: 36px; object-fit: contain; }
    .sb-brand-text { flex: 1; min-width: 0; }
    .sb-brand-title {
        font-size: 0.82rem; font-weight: 800; color: #ffffff !important;
        letter-spacing: 0.6px; line-height: 1.2;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .sb-brand-sub {
        font-size: 0.60rem; color: rgba(201,151,38,0.90) !important;
        font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase;
        margin-top: 2px; white-space: nowrap;
    }
    .sb-satria-badge { flex: 0 0 auto; }
    .sb-satria-badge img {
        height: 34px; width: auto;
        filter: drop-shadow(0 2px 8px rgba(229,179,61,0.55));
        opacity: 0.92;
    }
    .sb-brand-wrap::after {
        content: ''; display: block; height: 2px; border-radius: 999px;
        background: linear-gradient(90deg, rgba(201,151,38,0.80) 0%, rgba(229,179,61,0.28) 65%, transparent 100%);
        margin-top: 14px;
    }

    /* ================================================================
       USER PROFILE CARD
    ================================================================ */
    .sb-profile-card {
        margin: 10px 12px 6px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px; padding: 12px 13px;
        position: relative; overflow: hidden;
    }
    .sb-profile-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #c99726, #e5b33d 50%, transparent);
        border-radius: 14px 14px 0 0;
    }
    .sb-avatar-row { display: flex; align-items: flex-start; gap: 11px; }
    .sb-avatar {
        flex: 0 0 auto; width: 38px; height: 38px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.95rem; font-weight: 800; letter-spacing: -0.5px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.35);
    }
    .sb-avatar-sa {
        background: linear-gradient(135deg, #c99726, #e5b33d);
        color: #071527 !important; border: 2px solid rgba(255,255,255,0.25);
    }
    .sb-avatar-admin {
        background: linear-gradient(135deg, #1d4b8f, #2f61b0);
        color: #ffffff !important; border: 2px solid rgba(255,255,255,0.15);
    }
    .sb-user-info { flex: 1; min-width: 0; }
    .sb-user-name {
        font-size: 0.74rem; font-weight: 700; color: #ffffff !important;
        line-height: 1.3; word-break: break-word;
    }
    .sb-user-subline {
        font-size: 0.62rem; color: #94a3b8 !important;
        margin-top: 3px; line-height: 1.35;
    }
    .sb-role-badge {
        display: inline-flex; align-items: center; gap: 4px;
        margin-top: 7px; padding: 2px 9px; border-radius: 999px;
        font-size: 0.57rem; font-weight: 800; letter-spacing: 0.7px; text-transform: uppercase;
    }
    .sb-role-sa {
        background: linear-gradient(90deg, #c99726, #e5b33d);
        color: #071527 !important; box-shadow: 0 2px 8px rgba(201,151,38,0.4);
    }
    .sb-role-admin {
        background: rgba(29,75,143,0.55); color: #93c5fd !important;
        border: 1px solid rgba(59,130,246,0.35);
    }
    .sb-owner-tag {
        font-size: 0.56rem; color: rgba(229,179,61,0.70) !important;
        letter-spacing: 0.5px; text-transform: uppercase; margin-top: 3px; font-weight: 600;
    }

    /* ================================================================
       MENU SECTION LABELS
    ================================================================ */
    .sb-section-label {
        padding: 12px 16px 4px;
        font-size: 0.54rem; font-weight: 800; letter-spacing: 1.8px;
        text-transform: uppercase; color: rgba(201,151,38,0.60) !important;
        display: flex; align-items: center; gap: 7px; white-space: nowrap;
    }
    .sb-section-label::after {
        content: ''; flex: 1; height: 1px;
        background: rgba(201,151,38,0.14); border-radius: 1px;
    }

    /* ================================================================
       RADIO MENU RESTYLING
    ================================================================ */
    [data-testid='stSidebar'] .stRadio > label { display: none !important; }
    [data-testid='stSidebar'] .stRadio > div {
        gap: 1px !important;
        padding: 0 8px !important;
        flex-direction: column !important;
    }
    [data-testid='stSidebar'] .stRadio label {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 9px 12px !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease !important;
        border: 1px solid transparent !important;
        margin: 1px 0 !important;
        color: #94a3b8 !important;
        font-size: 0.80rem !important;
        font-weight: 500 !important;
        line-height: 1.3 !important;
        position: relative !important;
        overflow: hidden !important;
        width: 100% !important;
    }
    [data-testid='stSidebar'] .stRadio label > span:first-child { display: none !important; }
    [data-testid='stSidebar'] .stRadio label:hover {
        background: rgba(255,255,255,0.06) !important;
        color: #e2e8f0 !important;
        border-color: rgba(255,255,255,0.08) !important;
    }
    [data-testid='stSidebar'] .stRadio label:has(input[type="radio"]:checked) {
        background: rgba(201,151,38,0.12) !important;
        color: #f7d67e !important;
        border-color: rgba(201,151,38,0.28) !important;
        font-weight: 700 !important;
    }
    [data-testid='stSidebar'] .stRadio label:has(input[type="radio"]:checked)::before {
        content: '';
        position: absolute !important;
        left: 0; top: 20%; bottom: 20%;
        width: 3px !important;
        background: linear-gradient(180deg, #e5b33d, #c99726) !important;
        border-radius: 0 3px 3px 0 !important;
    }

    /* ================================================================
       LOGOUT BUTTON
    ================================================================ */
    [data-testid='stSidebar'] .stButton > button {
        background: rgba(220, 38, 38, 0.10) !important;
        color: #fca5a5 !important;
        border: 1px solid rgba(220, 38, 38, 0.28) !important;
        border-radius: 10px !important;
        font-size: 0.79rem !important;
        font-weight: 600 !important;
        padding: 0.45rem 1rem !important;
        width: 100% !important;
        transition: all 0.18s ease !important;
        box-shadow: none !important;
        margin: 0 !important;
    }
    [data-testid='stSidebar'] .stButton > button:hover {
        background: rgba(220, 38, 38, 0.22) !important;
        color: #f87171 !important;
        border-color: rgba(220, 38, 38, 0.48) !important;
        transform: none !important;
        box-shadow: 0 3px 10px rgba(220,38,38,0.20) !important;
    }

    /* ================================================================
       SIDEBAR FOOTER
    ================================================================ */
    .sb-footer {
        margin: 6px 12px 12px;
        padding: 9px 12px; border-radius: 10px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
    }
    .sb-footer-text {
        font-size: 0.59rem; color: rgba(148,163,184,0.55) !important;
        text-align: center; line-height: 1.65;
    }
    .sb-footer-text b { color: rgba(201,151,38,0.65) !important; }
    .sb-divider-line {
        height: 1px; background: rgba(201,151,38,0.10);
        border-radius: 1px; margin: 8px 12px;
    }

    /* ---- Hide replaced elements ---- */
    .satria-side-brand { display: none !important; }
    .user-pill { display: none !important; }
    [data-testid='stSidebar'] .stCaption { display: none !important; }

    /* ---- Collapse toggle button ---- */
    [data-testid="stSidebarCollapseButton"] button {
        background: rgba(201,151,38,0.12) !important;
        border: 1px solid rgba(201,151,38,0.22) !important;
        border-radius: 8px !important; color: #e5b33d !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover {
        background: rgba(201,151,38,0.25) !important;
        box-shadow: 0 3px 10px rgba(201,151,38,0.28) !important;
        transform: none !important;
    }

    /* ---- Preserve old pill classes (hidden but not removed) ---- */
    .user-pill .nama { font-weight: 700; font-size: 0.92rem; color: #ffffff; }
    .user-pill .badge-sa { display: none; }
    .user-pill .badge-admin { display: none; }
    .user-pill .subline { font-size: 0.72rem; color: #94a3b8; margin-top: 4px; }

    /* ---------- kartu & kontainer institusional ---------- */
    .gov-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(13, 35, 66, 0.05);
        margin-bottom: 16px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .gov-card:hover {
        box-shadow: 0 8px 22px rgba(13, 35, 66, 0.09);
    }

    /* ---------- hero banner dengan foto mako puslitbang ---------- */
    .satria-hero {
        position: relative;
        border-radius: 18px;
        overflow: hidden;
        margin-bottom: 18px;
        border: 1px solid rgba(229, 179, 61, 0.40);
        box-shadow: 0 12px 30px rgba(7, 21, 39, 0.28);
    }
    .satria-hero .foto {
        position: absolute;
        inset: 0;
        background-size: cover;
        background-position: center 30%;
        opacity: 0.52;
    }
    .satria-hero .tudung {
        position: absolute;
        inset: 0;
        background: linear-gradient(115deg, rgba(7, 21, 39, 0.94) 0%, rgba(13, 35, 66, 0.88) 50%, rgba(20, 53, 100, 0.75) 100%);
    }
    .satria-hero .isi {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 20px 26px;
        min-height: 140px;
    }
    .satria-hero .lgo {
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100px;
        height: 100px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.96);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.30);
    }
    .satria-hero .lgo img { max-width: 84px; max-height: 84px; }
    .satria-hero .lgo.satria {
        background: transparent;
        box-shadow: none;
        width: 115px;
        height: 115px;
    }
    .satria-hero .lgo.satria img {
        max-width: 115px;
        max-height: 115px;
        filter: drop-shadow(0 4px 14px rgba(229, 179, 61, 0.65));
    }
    .satria-hero .teks { flex: 1; min-width: 0; }
    .satria-hero .lembaga {
        color: var(--gov-gold-400);
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 2.2px;
        text-transform: uppercase;
    }
    .satria-hero .judul {
        color: #ffffff;
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1.22;
        margin-top: 3px;
    }
    .satria-hero .sub {
        color: #cbd5e1;
        font-size: 0.88rem;
        margin-top: 4px;
    }
    .satria-hero .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    .satria-hero .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(229, 179, 61, 0.40);
        color: #ffffff;
        font-size: 0.73rem;
        font-weight: 600;
        padding: 3px 12px;
        border-radius: 999px;
    }

    /* ---------- metrik statistik berwarna ---------- */
    div[data-testid='stMetric'] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 5px solid var(--gov-navy-700);
        border-radius: 14px;
        padding: 12px 16px;
        box-shadow: 0 4px 12px rgba(13, 35, 66, 0.06);
        transition: transform 0.14s ease, box-shadow 0.14s ease;
    }
    div[data-testid='stMetric']:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(13, 35, 66, 0.12);
    }
    div[data-testid='stMetricValue'] {
        color: var(--gov-navy-900);
        font-weight: 800;
        font-size: 1.45rem;
    }
    div[data-testid='stMetricLabel'] {
        color: var(--gov-slate-500);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ---------- tombol & input ---------- */
    .stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {
        background: linear-gradient(90deg, #143564, #1d4b8f);
        color: #ffffff;
        border: 0;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.88rem;
        padding: 0.5rem 1.2rem;
        box-shadow: 0 3px 10px rgba(20, 53, 100, 0.28);
        transition: all 0.15s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover, .stFormSubmitButton>button:hover {
        background: linear-gradient(90deg, #c99726, #e5b33d);
        color: #071527;
        box-shadow: 0 6px 18px rgba(201, 151, 38, 0.40);
        transform: translateY(-1px);
    }

    /* ---------- tabel & dataframe ---------- */
    [data-testid='stDataFrame'], [data-testid='stTable'] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.03);
    }

    /* ---------- lencana & status ---------- */
    .badge-aktif {
        background: #ecfdf5; color: #047857; font-weight: 700; font-size: 0.74rem;
        padding: 3px 10px; border-radius: 999px; border: 1px solid #a7f3d0;
    }
    .badge-nonaktif {
        background: #fef2f2; color: #b91c1c; font-weight: 700; font-size: 0.74rem;
        padding: 3px 10px; border-radius: 999px; border: 1px solid #fecaca;
    }
    .badge-subline {
        background: #eff6ff; color: #1d4ed8; font-weight: 600; font-size: 0.74rem;
        padding: 3px 10px; border-radius: 999px; border: 1px solid #bfdbfe;
    }

    /* ---------- footer institusional ---------- */
    .satria-kaki {
        margin-top: 24px;
        padding: 16px 20px;
        border-radius: 14px;
        background: linear-gradient(90deg, #071527 0%, #0d2342 60%, #143564 100%);
        color: #cbd5e1;
        font-size: 0.80rem;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 4px 14px rgba(7, 21, 39, 0.15);
    }
    .satria-kaki img { height: 38px; width: auto; }
    .satria-kaki .g { flex: 1; }
    .satria-kaki b { color: var(--gov-gold-300); }
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def kop(judul_teks, sub_teks="", subline_label=None):
    """Header banner institusi dengan latar resmi Gedung Mako Puslitbang Polri terbaru."""
    logo = _data_uri("puslitbang_logo.png")
    satria = _data_uri("satria_logo.png") or _data_uri("satria_badge.png")
    # Mengutamakan aset resmi Gedung Mako Puslitbang Polri Terbaru
    foto = _data_uri("MAKO PUSLITBANG TERBARU.jpeg") or _data_uri("gedung_band.jpg") or _data_uri("bg_hero.png")
    hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][date.today().weekday()]

    h = ["<div class='satria-hero'>"]
    if foto:
        h.append("<div class='foto' style=\"background-image:url('%s')\"></div>" % foto)
    h.append("<div class='tudung'></div><div class='isi'>")
    h.append("<div class='lgo'>%s</div>" % (("<img src='%s' alt='Puslitbang Polri'/>" % logo) if logo else "<b>POLRI</b>"))
    h.append("<div class='teks'>")
    h.append("<div class='lembaga'>Pusat Penelitian dan Pengembangan Polri</div>")
    h.append("<div class='judul'>%s</div>" % judul_teks)
    if sub_teks:
        h.append("<div class='sub'>%s</div>" % sub_teks)
    h.append("<div class='chip-row'>")
    h.append("<span class='chip'>📅 %s, %s</span>" % (hari, tgl_id(date.today().isoformat())))
    h.append("<span class='chip'>🔒 Sistem Pengendalian Internal SATRIA</span>")
    h.append("<span class='chip'>🎯 Tahun Anggaran 2026</span>")
    if subline_label:
        h.append("<span class='chip' style='border-color:#f7d67e; color:#f7d67e;'>🏢 Unit: %s</span>" % subline_label)
    h.append("</div>")
    h.append("</div>")
    h.append("<div class='lgo satria'>%s</div>" % (("<img src='%s' alt='SATRIA'/>" % satria) if satria else ""))
    h.append("</div></div>")
    st.markdown("".join(h), unsafe_allow_html=True)


def tiga_pilar():
    """Tiga instrumen SATRIA (SOP, Risk Register, Kartu Kendali KPA)."""
    st.markdown("""
<div style="display:flex; gap:12px; flex-wrap:wrap; margin:10px 0 16px;">
  <div style="flex:1 1 220px; background:#fff; border:1px solid #e2e8f0; border-left:5px solid #143564; border-radius:12px; padding:14px; box-shadow:0 3px 10px rgba(0,0,0,0.04);">
    <h4 style="margin:0 0 6px; color:#0d2342; font-size:0.96rem;">1. SOP Pra-DIPA &amp; Transisi</h4>
    <p style="margin:0; color:#64748b; font-size:0.80rem; line-height:1.4;">Kesiapan pengadaan sejak dini dan mitigasi kepemimpinan kewenangan KPA.</p>
  </div>
  <div style="flex:1 1 220px; background:#fff; border:1px solid #e2e8f0; border-left:5px solid #059669; border-radius:12px; padding:14px; box-shadow:0 3px 10px rgba(0,0,0,0.04);">
    <h4 style="margin:0 0 6px; color:#0d2342; font-size:0.96rem;">2. Risk Register Kinerja</h4>
    <p style="margin:0; color:#64748b; font-size:0.80rem; line-height:1.4;">Matriks 5x5 risiko, skor Kemungkinan x Dampak, eskalasi merah 1x24 jam.</p>
  </div>
  <div style="flex:1 1 220px; background:#fff; border:1px solid #e2e8f0; border-left:5px solid #c99726; border-radius:12px; padding:14px; box-shadow:0 3px 10px rgba(0,0,0,0.04);">
    <h4 style="margin:0 0 6px; color:#0d2342; font-size:0.96rem;">3. Kartu Kendali Bulanan KPA</h4>
    <p style="margin:0; color:#64748b; font-size:0.80rem; line-height:1.4;">Kendali keputusan KPA, capaian 6 paket sasaran, dan peringatan dini.</p>
  </div>
</div>
""", unsafe_allow_html=True)


def foto_bangunan(keterangan="Gedung Markas Komando Puslitbang Polri"):
    """Bingkai foto resmi Gedung Mako Puslitbang Polri."""
    b = _data_uri("MAKO PUSLITBANG TERBARU.jpeg") or _data_uri("gedung_band.jpg")
    if not b:
        return
    st.markdown(
        f"<div style='border-radius:14px; overflow:hidden; border:1px solid #cbd5e1; box-shadow:0 6px 18px rgba(7,21,39,0.12); margin-bottom:12px;'>"
        f"<img src='{b}' alt='{keterangan}' style='width:100%; display:block;'/>"
        f"<div style='background:linear-gradient(90deg, #071527, #143564); color:#fff; font-size:0.80rem; font-weight:600; padding:8px 14px;'>"
        f"🏛️ {keterangan}</div></div>",
        unsafe_allow_html=True)


def galeri(judul_galeri="Galeri Dokumentasi Kegiatan & Uji Coba Puslitbang Polri"):
    """Ditiadakan sesuai arahan pengguna."""
    return


def kaki():
    """Catatan kaki resmi aplikasi."""
    pb = _data_uri("puslitbang_logo.png")
    st.markdown(
        "<div class='satria-kaki'>%s<div class='g'>"
        "<b>Dashboard Pengendalian &amp; Keputusan SATRIA Puslitbang Polri</b> — "
        "Sistem Tata Kelola Akselerasi Kinerja &amp; Keuangan Berbasis Risiko.<br/>"
        "“Kepastian Regulasi, Kemudahan Eksekusi” | Arsitektur Single Super Admin &amp; Multi-Admin Terisolasi. "
        "Jejak audit aktif mencatat seluruh operasional.</div></div>"
        % (("<img src='%s' alt='Puslitbang Polri'/>" % pb) if pb else ""),
        unsafe_allow_html=True)


def stempel_data():
    r = db.one("SELECT MAX(waktu) AS w FROM audit WHERE aksi LIKE 'Impor%' OR aksi LIKE 'Perbarui%' OR aksi LIKE 'Tambah%'")
    if r and r["w"]:
        st.caption("⏱️ Posisi pembaruan data sistem terakhir: **%s** — tersinkronisasi langsung ke seluruh ruang kerja." % r["w"])
    else:
        st.caption("⏱️ Posisi data tersinkronisasi basis data lokal.")


AUTO_REFRESH_DETIK = 60
tema()

# ------------------------------------------------------------------ utilitas angka & format ----
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def rp(v):
    try:
        return "Rp" + format(int(round(float(v))), ",d").replace(",", ".")
    except (TypeError, ValueError):
        return "-"


def id_num(x, des=2):
    return ("{:." + str(des) + "f}").format(float(x)).replace(".", ",")


def tgl_id(iso):
    try:
        d = datetime.strptime(str(iso)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return str(iso)
    return "%d %s %d" % (d.day, BULAN[d.month - 1], d.year)


def em(level):
    return {"Merah": "🔴", "Kuning": "🟡", "Hijau": "🟢"}.get(level, "⚪")


def level_dari_skor(skor):
    merah = db.float_setelan("risiko_merah", 10)
    kuning = db.float_setelan("risiko_kuning", 5)
    if skor >= merah:
        return "Merah"
    if skor >= kuning:
        return "Kuning"
    return "Hijau"


def boleh_ubah_paket(no_paket, peran_or_user, paket_id=None, subline=None):
    """Pemeriksaan hak akses backend untuk pembaruan paket sasaran."""
    # Menangani parameter jika dipanggil dengan objek user maupun peran string lama
    if isinstance(peran_or_user, dict):
        user = peran_or_user
        if db.is_super_admin(user):
            return True
        p = db.one("SELECT * FROM paket WHERE no=?", (no_paket,))
        if not p:
            return False
        user_subline = user.get("subline") or ""
        user_pkt = user.get("paket_id") or ""
        if p.get("subline") and p.get("subline") == user_subline:
            return True
        if str(no_paket) in [x.strip() for x in user_pkt.split(",") if x.strip()]:
            return True
        return False
    else:
        peran = str(peran_or_user).strip()
        if peran in ("SUPER ADMIN", "kpa", "urkeu"):
            return True
        if peran in ("ADMIN", "ppk"):
            if paket_id and str(no_paket) in [x.strip() for x in str(paket_id).split(",") if x.strip()]:
                return True
            if subline:
                p = db.one("SELECT subline FROM paket WHERE no=?", (no_paket,))
                if p and p.get("subline") == subline:
                    return True
        return False


# ------------------------------------------------------------------ halaman masuk ----
def halaman_masuk():
    kop("Sistem Pengendalian & Pengambilan Keputusan SATRIA",
        "Pusat Penelitian dan Pengembangan Polri — Portal Masuk Resmi Single Super Admin & Multi-Admin")
    tiga_pilar()

    kiri, kanan = st.columns([5, 4])
    with kiri:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:22px; box-shadow:0 6px 20px rgba(7,21,39,0.06); margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                <span style="font-size:1.3rem;">🔐</span>
                <span style="font-weight:800; font-size:1.15rem; color:#0d2342;">Masuk ke Sistem SATRIA</span>
            </div>
            <p style="color:#64748b; font-size:0.83rem; margin-top:-6px; margin-bottom:16px;">
                Sistem otomatis mendeteksi role akun (Super Admin atau Admin Subline). Subline ditetapkan langsung oleh Super Admin.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_masuk"):
            nama_pengguna = st.text_input("Nama pengguna (Username)", placeholder="Masukkan username Anda...")
            sandi = st.text_input("Kata sandi (Password)", type="password", placeholder="Masukkan kata sandi...")
            masuk = st.form_submit_button("Masuk Aplikasi")

        if masuk:
            hasil = db.verifikasi_login(nama_pengguna, sandi)
            if hasil:
                st.session_state["pengguna"] = dict(hasil)
                is_sa = db.is_super_admin(hasil)
                st.session_state["menu_terpilih"] = "Dashboard Utama" if is_sa else "Dashboard Admin"
                db.audit(hasil["nama_pengguna"], "Masuk aplikasi",
                         f"Peran: {hasil['peran']} | Subline: {hasil.get('subline', '-')}")
                st.rerun()
            else:
                st.error("Nama pengguna atau kata sandi salah (akun tidak aktif juga ditolak oleh sistem).")

        st.info("💡 **Akun Terdaftar:**\n"
                "- **Super Admin (Pemilik Sistem):** `kpa` (Akses Penuh Seluruh Subline & Konfigurasi)\n"
                "- **Multi-Admin Subline:** `kristo` (PPK PUSLITBANG POLRI), `budi` (SUBLINE UNIT 02), `andi` (SUBLINE UNIT 03), `urkeu`, `pokja`, `ppk1`–`ppk5`\n"
                "- **Kata sandi bawaan:** `satria2026`")

    with kanan:
        foto_bangunan("Gedung Markas Komando Puslitbang Polri — Rawamangun, Jakarta Timur")

    st.write("")
    kaki()


# ------------------------------------------------------------------ proteksi sesi ----
if "pengguna" not in st.session_state:
    st.session_state["pengguna"] = None

if st.session_state["pengguna"] is None:
    halaman_masuk()
    st.stop()

user = st.session_state["pengguna"]
is_sa = db.is_super_admin(user)
peran = user.get("peran", "ADMIN")
subline_user = user.get("subline") or "PUSLITBANG POLRI"

# ------------------------------------------------------------------ sidebar berdasarkan role ----
_pb = _data_uri("puslitbang_logo.png")
_st = _data_uri("satria_logo.png") or _data_uri("satria_badge.png")

# ── BRANDING HEADER ──────────────────────────────────────────────────────────
_logo_html = ("<img src=\'%s\' alt=\'Puslitbang Polri\'/>" % _pb) if _pb else "<b style=\'color:#c99726;font-size:1.2rem;\'>POLRI</b>"
_satria_html = ("<img src=\'%s\' alt=\'SATRIA\'/>" % _st) if _st else ""
st.sidebar.markdown(f"""
<div class=\'sb-brand-wrap\'>
  <div class=\'sb-brand-inner\'>
    <div class=\'sb-logo-box\'>{_logo_html}</div>
    <div class=\'sb-brand-text\'>
      <div class=\'sb-brand-title\'>SATRIA POLRI</div>
      <div class=\'sb-brand-sub\'>Dashboard Pengendalian</div>
    </div>
    <div class=\'sb-satria-badge\'>{_satria_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── USER PROFILE CARD ─────────────────────────────────────────────────────────
_nama_user = user["nama"]
_initials = "".join([w[0].upper() for w in _nama_user.split() if w][:2]) or "U"
_avatar_class = "sb-avatar-sa" if is_sa else "sb-avatar-admin"
_badge_class  = "sb-role-sa"   if is_sa else "sb-role-admin"
_badge_icon   = "🛡️" if is_sa else "👤"
_badge_label  = "SUPER ADMIN" if is_sa else "ADMIN"
_owner_tag    = "<div class=\'sb-owner-tag\'>SYSTEM OWNER · AKSES PENUH</div>" if is_sa else ""

st.sidebar.markdown(f"""
<div class=\'sb-profile-card\'>
  <div class=\'sb-avatar-row\'>
    <div class=\'sb-avatar {_avatar_class}\'>{_initials}</div>
    <div class=\'sb-user-info\'>
      <div class=\'sb-user-name\'>{_nama_user}</div>
      <div class=\'sb-user-subline\'>🏢 {subline_user}</div>
      <div class=\'sb-role-badge {_badge_class}\'>{_badge_icon} {_badge_label}</div>
      {_owner_tag}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── MENU DEFINITIONS ──────────────────────────────────────────────────────────
# Super Admin: 8 menu khusus SA + seluruh menu operasional
MENU_SUPER = [
    "Dashboard Utama",
    "Manajemen Admin",
    "Manajemen Subline",
    "Seluruh Data",
    "Laporan Keseluruhan",
    "Aktivitas Pengguna",
    "Audit Log",
    "Pengaturan Sistem",
    # Menu operasional lama tetap dipertahankan
    "Ringkasan KPA",
    "Anggaran & Paket",
    "Manajemen Risiko",
    "Kontrak",
    "Milestone & Lampiran",
    "Keputusan KPA",
    "Impor Data (SAKTI/OM-SPAN)",
    "Pengaturan & Audit",
]

# Admin biasa: menu operasional terisolasi subline
MENU_ADMIN = [
    "Dashboard Admin",
    "Anggaran & Paket",
    "Manajemen Risiko",
    "Kontrak",
    "Milestone & Lampiran",
    "Keputusan KPA",
    "Impor Data (SAKTI/OM-SPAN)",
    "Profil & Akun",
]

# ── MENU RENDERING — GROUPED SECTIONS ────────────────────────────────────────
daftar_menu = MENU_SUPER if is_sa else MENU_ADMIN
default_idx = 0
if "menu_terpilih" in st.session_state and st.session_state["menu_terpilih"] in daftar_menu:
    default_idx = daftar_menu.index(st.session_state["menu_terpilih"])

if is_sa:
    # SUPER ADMIN — Section label: PUSAT KENDALI
    st.sidebar.markdown("<div class=\'sb-section-label\'>⬡ PUSAT KENDALI</div>", unsafe_allow_html=True)
    # Section label: MANAJEMEN DATA (shown as static HTML, radio still controls navigation)
    # We render one combined radio but add visual section dividers via markdown
    pilihan = st.sidebar.radio(
        "Navigasi Menu",
        daftar_menu,
        index=default_idx,
        format_func=lambda x: {
            "Dashboard Utama":            "🏠  Dashboard Utama",
            "Manajemen Admin":            "👥  Manajemen Admin",
            "Manajemen Subline":          "🏢  Manajemen Subline",
            "Seluruh Data":               "🗄️  Seluruh Data",
            "Laporan Keseluruhan":        "📊  Laporan Keseluruhan",
            "Aktivitas Pengguna":         "⚡  Aktivitas Pengguna",
            "Audit Log":                  "🔍  Audit Log",
            "Pengaturan Sistem":          "⚙️  Pengaturan Sistem",
            "Ringkasan KPA":              "📋  Ringkasan KPA",
            "Anggaran & Paket":           "💰  Anggaran & Paket",
            "Manajemen Risiko":           "🎯  Manajemen Risiko",
            "Kontrak":                    "📄  Kontrak",
            "Milestone & Lampiran":       "✅  Milestone & Lampiran",
            "Keputusan KPA":              "🔔  Keputusan KPA",
            "Impor Data (SAKTI/OM-SPAN)": "⬆️  Impor Data (SAKTI/OM-SPAN)",
            "Pengaturan & Audit":         "🔐  Pengaturan & Audit",
        }.get(x, x)
    )
else:
    # ADMIN BIASA — Section label
    st.sidebar.markdown("<div class=\'sb-section-label\'>▸ MENU UTAMA</div>", unsafe_allow_html=True)
    pilihan = st.sidebar.radio(
        "Navigasi Menu",
        daftar_menu,
        index=default_idx,
        format_func=lambda x: {
            "Dashboard Admin":            "🏠  Dashboard",
            "Anggaran & Paket":           "💰  Anggaran & Paket",
            "Manajemen Risiko":           "🎯  Manajemen Risiko",
            "Kontrak":                    "📄  Kontrak",
            "Milestone & Lampiran":       "✅  Milestone & Lampiran",
            "Keputusan KPA":              "🔔  Keputusan KPA",
            "Impor Data (SAKTI/OM-SPAN)": "⬆️  Impor Data",
            "Profil & Akun":              "👤  Profil & Akun",
        }.get(x, x)
    )

st.session_state["menu_terpilih"] = pilihan

# ── DIVIDER + LOGOUT ──────────────────────────────────────────────────────────
st.sidebar.markdown("<div class=\'sb-divider-line\'></div>", unsafe_allow_html=True)
if st.sidebar.button("🚪  Keluar Aplikasi", key="btn_logout"):
    db.audit(user["nama_pengguna"], "Keluar aplikasi", f"Sesi berakhir untuk {user['nama_pengguna']}")
    st.session_state["pengguna"] = None
    st.session_state["menu_terpilih"] = None
    st.rerun()

# ── SIDEBAR FOOTER ────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class=\'sb-footer\'>
  <div class=\'sb-footer-text\'>
    <b>SATRIA</b> Puslitbang Polri<br/>
    v2.0 · 2026 · Mode LAN/Offline<br/>
    <span style=\'opacity:0.5;\'>Single SA + Multi-Admin</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ FUNGSI HALAMAN SUPER ADMIN ----

def hal_super_dashboard():
    """1. Dashboard Utama Khusus Super Admin: Statistik Eksekutif, Lintas Subline, & Peringatan."""
    kop("Dashboard Utama Super Admin",
        "Pengendali Penuh Sistem SATRIA — Monitoring Komprehensif Seluruh Admin & Subline Puslitbang Polri",
        "PUSAT KENDALI EKSEKUTIF")
    stempel_data()

    # Data ringkasan aplikasi
    semua_pengguna = db.ambil_semua_pengguna()
    total_admin = sum(1 for p in semua_pengguna if not db.is_super_admin(p))
    total_aktif = sum(1 for p in semua_pengguna if p["aktif"] == 1)
    total_nonaktif = sum(1 for p in semua_pengguna if p["aktif"] == 0)
    semua_subline = db.daftar_subline()
    subline_aktif = sum(1 for s in semua_subline if s["aktif"] == 1)

    agg = db.rows("SELECT * FROM anggaran WHERE kategori='AGREGAT' ORDER BY id DESC")
    a = agg[0] if agg else {"pagu": 0, "realisasi": 0, "sisa": 0, "persen": 0.0, "periode": "Juli 2026"}

    pakets = db.rows("SELECT * FROM paket ORDER BY no")
    kontraks = db.rows("SELECT * FROM kontrak ORDER BY id")
    peringatan = db.daftar_peringatan()
    n_merah = sum(1 for p in peringatan if p["level"] == "Merah")
    n_kuning = sum(1 for p in peringatan if p["level"] == "Kuning")

    # Baris Kartu Statistik 1: Anggaran & Keuangan
    st.markdown("##### 💼 Posisi Anggaran & Kinerja Aplikasi Global")
    c1 = st.columns(4)
    c1[0].metric("Pagu TA 2026", rp(a["pagu"]), help="Total Pagu Agregat Satker Puslitbang Polri")
    c1[1].metric("Realisasi Kumulatif", rp(a["realisasi"]), f"{id_num(a['persen'])}% dari pagu")
    c1[2].metric("Sisa Anggaran", rp(a["sisa"]))
    c1[3].metric("Peringatan Dini Sistem", f"{n_merah} Merah / {n_kuning} Kuning",
                 delta="Wajib Eskalasi KPA" if n_merah > 0 else "Terkendali",
                 delta_color="inverse" if n_merah > 0 else "normal")

    # Baris Kartu Statistik 2: Pengguna & Arsitektur Subline
    st.markdown("##### 👥 Manajemen Pengguna & Subline Aktif")
    c2 = st.columns(4)
    c2[0].metric("Total Admin Terdaftar", total_admin, help="Jumlah akun Admin biasa (dapat bertambah tanpa batas)")
    c2[1].metric("Subline Unit Aktif", subline_aktif, help="Jumlah unit kerja subline aktif yang mengisolasi data")
    c2[2].metric("Akun Pengguna Aktif", total_aktif)
    c2[3].metric("Akun Dinonaktifkan", total_nonaktif)

    # Grafik Perkembangan Data & Statistik per Subline
    st.divider()
    k1, k2 = st.columns([6, 5])
    with k1:
        st.subheader("📊 Statistik Capaian Data Berdasarkan Subline")
        data_sbl = []
        for s in semua_subline:
            stt = db.ambil_statistik_subline(s["nama"], is_super=False)
            data_sbl.append({
                "Subline / Unit": s["nama"],
                "Admin": s["total_admin"],
                "Paket": stt["total_paket"],
                "Pagu (Rp)": rp(stt["total_pagu"]),
                "Realisasi (Rp)": rp(stt["total_realisasi"]),
                "Capaian %": f"{id_num(stt['persen_capaian'])}%",
                "Kontrak": stt["total_kontrak"],
                "Risiko Merah": stt["risiko_merah"],
            })
        st.dataframe(pd.DataFrame(data_sbl), hide_index=True, width='stretch')

    with k2:
        st.subheader("📈 Capaian 6 Paket Sasaran Utama")
        cap_chart = []
        for p in pakets:
            cp = (p["realisasi"] / p["target"] * 100) if p["target"] else 0
            cap_chart.append({"Paket": f"Paket {p['no']} - {p['nama'][:20]}", "Capaian %": cp})
        if cap_chart:
            st.bar_chart(pd.DataFrame(cap_chart).set_index("Paket"), height=260)

    # Aktivitas Admin Terbaru & Berkas Impor
    st.divider()
    k3, k4 = st.columns([6, 5])
    with k3:
        st.subheader("⚡ Aktivitas Admin Terbaru (Real-Time)")
        audit_top = db.ambil_riwayat_aktivitas(batas=8)
        if audit_top:
            st.dataframe(pd.DataFrame([{
                "Waktu": a["waktu"], "Pengguna": a["pengguna"],
                "Aksi": a["aksi"], "Detail": a["detail"]
            } for a in audit_top]), hide_index=True, width='stretch')
        else:
            st.caption("Belum ada aktivitas tercatat.")

    with k4:
        st.subheader("📥 Data Terbaru yang Masuk")
        file_r = db.file_impor_terakhir("realisasi")
        file_k = db.file_impor_terakhir("kontrak")
        if file_r:
            st.success(f"**Laporan Realisasi:** {file_r['nama_file']} ({file_r['format']})\n\n"
                       f"Periode: {file_r['periode']} | Oleh: {file_r['pengimpor']} | Waktu: {file_r['waktu']}")
        if file_k:
            st.info(f"**Monitoring Kontrak:** {file_k['nama_file']} ({file_k['format']})\n\n"
                    f"Ringkasan: {file_k['ringkasan']} | Oleh: {file_k['pengimpor']} | Waktu: {file_k['waktu']}")
        if not file_r and not file_k:
            st.caption("Belum ada berkas impor yang tersimpan.")


def hal_manajemen_admin():
    """2. Manajemen Admin Khusus Super Admin: Tambah, Edit, Detail, Reset Sandi, Aktif/Nonaktif, Hapus."""
    kop("Manajemen Admin & Hak Akses",
        "Super Admin mengelola identitas, penetapan subline, status akun, dan kata sandi seluruh admin.",
        "SUPER ADMIN")

    # Summary bar
    users_all = db.ambil_semua_pengguna()
    total_adm = sum(1 for u in users_all if not db.is_super_admin(u))
    aktif_cnt = sum(1 for u in users_all if u["aktif"] == 1 and not db.is_super_admin(u))
    non_cnt = sum(1 for u in users_all if u["aktif"] == 0 and not db.is_super_admin(u))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Admin Biasa", total_adm)
    m2.metric("Admin Aktif", aktif_cnt)
    m3.metric("Admin Nonaktif", non_cnt)
    m4.metric("Super Admin", 1, help="Hanya ada SATU akun Super Admin di sistem")

    st.write("")

    # Form Tambah Admin Baru
    with st.expander("➕ Tambah Akun Admin Baru", expanded=False):
        st.markdown("**Buat akun Admin operasional baru.** Role otomatis ditetapkan sebagai **ADMIN**.")
        daftar_sub_aktif = [s["nama"] for s in db.daftar_subline(hanya_aktif=True)]
        with st.form("form_tambah_admin"):
            t1, t2 = st.columns(2)
            new_user = t1.text_input("Username (nama pengguna unik)*", placeholder="mis. kristo, budi, andi...")
            new_nama = t2.text_input("Nama Lengkap Admin*", placeholder="mis. IPTU Kristo, S.H.")
            t3, t4 = st.columns(2)
            new_subline = t3.selectbox("Subline / Unit Kerja Terikat*", daftar_sub_aktif if daftar_sub_aktif else ["PPK PUSLITBANG POLRI"])
            new_sandi = t4.text_input("Kata Sandi Awal*", type="password", value="satria2026")
            new_paket = st.text_input("Paket Sasaran Tanggung Jawab (opsional)", placeholder="mis. 2,3 atau kosongkan bila umum")
            simpan_baru = st.form_submit_button("Simpan Admin Baru")

        if simpan_baru:
            try:
                db.tambah_admin(new_user, new_nama, new_sandi, new_subline, peran="ADMIN",
                                paket_id=new_paket, aktor=user["nama_pengguna"])
                st.success(f"Akun Admin '{new_user}' ({new_nama}) berhasil didaftarkan pada Subline '{new_subline}'.")
                st.rerun()
            except Exception as exc:
                st.error(f"Gagal menambahkan admin: {exc}")

    st.subheader("📋 Daftar Seluruh Akun Admin")

    # Filter & Pencarian
    sublines_filter = ["Semua Subline"] + [s["nama"] for s in db.daftar_subline()]
    f1, f2, f3 = st.columns([4, 4, 3])
    cari_txt = f1.text_input("🔍 Cari Admin (Nama / Username / Subline)", placeholder="Ketik kata kunci...")
    pilih_filter_sub = f2.selectbox("Filter Berdasarkan Subline", sublines_filter)
    pilih_filter_stat = f3.selectbox("Filter Status Akun", ["Semua Status", "Aktif", "Nonaktif"])

    daftar_tampil = db.ambil_semua_pengguna(filter_subline=pilih_filter_sub,
                                           filter_status=pilih_filter_stat,
                                           cari=cari_txt)

    tabel_data = []
    for idx, u in enumerate(daftar_tampil):
        is_su = db.is_super_admin(u)
        role_label = "🛡️ SUPER ADMIN" if is_su else "👤 ADMIN"
        stat_label = "🟢 Aktif" if u["aktif"] else "🔴 Nonaktif"
        tabel_data.append({
            "No": idx + 1,
            "Nama Admin": u["nama"],
            "Username": u["nama_pengguna"],
            "Subline": u.get("subline") or "-",
            "Role": role_label,
            "Status Akun": stat_label,
            "Terakhir Login": u.get("terakhir_login") or "Belum login",
            "Tanggal Dibuat": tgl_id(u.get("created_at") or "-"),
        })

    st.dataframe(pd.DataFrame(tabel_data), hide_index=True, width='stretch')

    # Aksi & Detail Admin
    st.divider()
    st.subheader("⚙️ Aksi & Detail Akun Admin")
    opsi_admin = [u["nama_pengguna"] for u in daftar_tampil]
    if not opsi_admin:
        st.info("Tidak ada admin yang sesuai dengan kriteria filter.")
        return

    pilih_u = st.selectbox("Pilih Akun yang Dikelola", opsi_admin,
                           format_func=lambda x: f"{x} — {next(u['nama'] for u in daftar_tampil if u['nama_pengguna']==x)} ({next(u.get('subline','-') for u in daftar_tampil if u['nama_pengguna']==x)})")
    user_target = db.ambil_pengguna(pilih_u)
    target_is_sa = db.is_super_admin(user_target)

    tab_det, tab_edt, tab_pwd, tab_del = st.tabs(["📄 Detail & Statistik", "✏️ Edit Admin & Subline", "🔑 Reset Password", "⚠️ Status & Hapus"])

    with tab_det:
        det = db.ambil_detail_admin(pilih_u)
        kd1, kd2 = st.columns([5, 6])
        with kd1:
            st.markdown(f"**Identitas Akun:**\n\n"
                        f"- **Username:** `{user_target['nama_pengguna']}`\n"
                        f"- **Nama Lengkap:** {user_target['nama']}\n"
                        f"- **Role:** {'SUPER ADMIN' if target_is_sa else 'ADMIN'}\n"
                        f"- **Subline:** {user_target.get('subline') or '-'}\n"
                        f"- **Status Akun:** {'Aktif' if user_target['aktif'] else 'Nonaktif'}\n"
                        f"- **Terakhir Login:** {user_target.get('terakhir_login') or 'Belum pernah login'}\n"
                        f"- **Tanggal Dibuat:** {user_target.get('created_at') or '-'}")
        with kd2:
            st.markdown(f"**Statistik Data Milik Admin ({user_target.get('subline', '-')}):**")
            sd1, sd2 = st.columns(2)
            sd1.metric("Total Pagu Paket", rp(det["total_pagu"]))
            sd2.metric("Total Realisasi", rp(det["total_realisasi"]))
            sd1.metric("Jumlah Kontrak", det["total_kontrak"])
            sd2.metric("Nilai Kontrak", rp(det["total_kontrak_nilai"]))

        if det["paket"]:
            st.markdown("**Paket Sasaran yang Dikelola:**")
            st.dataframe(pd.DataFrame([{
                "No": p["no"], "Paket": p["nama"], "Pagu": rp(p["pagu"]),
                "Realisasi": rp(p["realisasi"]), "Catatan": p["catatan"] or "-"
            } for p in det["paket"]]), hide_index=True, width='stretch')

        if det["aktivitas"]:
            st.markdown("**Aktivitas Terakhir:**")
            st.dataframe(pd.DataFrame([{
                "Waktu": a["waktu"], "Aksi": a["aksi"], "Detail": a["detail"]
            } for a in det["aktivitas"][:8]]), hide_index=True, width='stretch')

    with tab_edt:
        with st.form("form_edit_admin"):
            ed_nama = st.text_input("Nama Lengkap Admin", value=user_target["nama"])
            sub_list = [s["nama"] for s in db.daftar_subline()]
            idx_sub = sub_list.index(user_target["subline"]) if user_target.get("subline") in sub_list else 0
            ed_subline = st.selectbox("Subline / Unit Kerja", sub_list, index=idx_sub)
            ed_paket = st.text_input("Paket Tanggung Jawab", value=user_target.get("paket_id") or "")
            ed_aktif = st.checkbox("Status Akun Aktif", value=bool(user_target["aktif"]), disabled=target_is_sa)
            if target_is_sa:
                st.caption("ℹ️ Akun Super Admin wajib selalu aktif dan tidak dapat dinonaktifkan.")
            simpan_edit = st.form_submit_button("Simpan Perubahan Admin")

        if simpan_edit:
            try:
                db.edit_admin(pilih_u, ed_nama, ed_subline, ed_aktif, paket_id=ed_paket,
                              peran="SUPER ADMIN" if target_is_sa else "ADMIN", aktor=user["nama_pengguna"])
                st.success(f"Perubahan akun '{pilih_u}' berhasil disimpan.")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memperbarui: {e}")

    with tab_pwd:
        with st.form("form_reset_sandi"):
            st.markdown(f"Reset kata sandi untuk akun **{pilih_u}**:")
            pwd_baru = st.text_input("Kata Sandi Baru*", type="password")
            pwd_ulang = st.text_input("Ulangi Kata Sandi Baru*", type="password")
            btn_reset = st.form_submit_button("Terapkan Kata Sandi Baru")

        if btn_reset:
            if pwd_baru != pwd_ulang:
                st.error("Ketikan kata sandi baru tidak sama.")
            elif len(pwd_baru.strip()) < 6:
                st.error("Kata sandi minimal 6 karakter.")
            else:
                db.reset_sandi_admin(pilih_u, pwd_baru.strip(), aktor=user["nama_pengguna"])
                st.success(f"Kata sandi untuk '{pilih_u}' berhasil diperbarui.")

    with tab_del:
        if target_is_sa:
            st.warning("🛡️ Akun ini adalah Super Admin utama. Super Admin tidak dapat dinonaktifkan atau dihapus.")
        else:
            k_act1, k_act2 = st.columns(2)
            with k_act1:
                status_sekarang = user_target["aktif"]
                label_btn = "🔴 Nonaktifkan Akun" if status_sekarang else "🟢 Aktifkan Akun"
                if st.button(label_btn, key=f"tgl_{pilih_u}"):
                    db.toggle_status_admin(pilih_u, not status_sekarang, aktor=user["nama_pengguna"])
                    st.success(f"Status akun '{pilih_u}' berhasil diubah.")
                    st.rerun()

            with k_act2:
                if st.button(f"🗑️ Hapus Akun {pilih_u}", key=f"del_{pilih_u}"):
                    try:
                        db.hapus_admin(pilih_u, aktor=user["nama_pengguna"])
                        st.success(f"Akun '{pilih_u}' berhasil dihapus.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus: {e}")


def hal_manajemen_subline():
    """3. Manajemen Subline Khusus Super Admin: Kelola Unit Kerja, Tambah, Edit, & Statistik."""
    kop("Manajemen Subline & Unit Kerja",
        "Super Admin menentukan subline utama masing-masing admin untuk memastikan data antaradmin terisolasi.",
        "SUPER ADMIN")

    # Form Tambah Subline Baru
    with st.expander("➕ Tambah Subline / Unit Kerja Baru", expanded=False):
        with st.form("form_subline_baru"):
            s1, s2 = st.columns(2)
            kode_s = s1.text_input("Kode Subline*", placeholder="mis. SUBLINE-04, LAB-PENGUJIAN...")
            nama_s = s2.text_input("Nama Subline / Unit Kerja*", placeholder="mis. SUBLINE UNIT 04, Laboratorium Balistik...")
            ket_s = st.text_area("Keterangan Unit Kerja", placeholder="Deskripsi tugas dan fungsi unit...")
            simpan_sub = st.form_submit_button("Simpan Subline Baru")

        if simpan_sub:
            try:
                db.tambah_subline(kode_s, nama_s, ket_s, aktor=user["nama_pengguna"])
                st.success(f"Subline '{nama_s}' berhasil didaftarkan.")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menambah subline: {e}")

    st.subheader("🏛️ Daftar Subline & Distribusi Data")
    sublines = db.daftar_subline()
    df_sub = pd.DataFrame([{
        "ID": s["id"],
        "Kode": s["kode"],
        "Nama Subline": s["nama"],
        "Keterangan": s["keterangan"] or "-",
        "Jumlah Admin": s["total_admin"],
        "Jumlah Paket": s["total_paket"],
        "Jumlah Kontrak": s["total_kontrak"],
        "Status": "🟢 Aktif" if s["aktif"] else "🔴 Nonaktif",
        "Tanggal Dibuat": tgl_id(s.get("created_at") or "-")
    } for s in sublines])
    st.dataframe(df_sub, hide_index=True, width='stretch')

    st.divider()
    st.subheader("✏️ Edit Subline Terdaftar")
    pilih_sub_id = st.selectbox("Pilih Subline untuk Diedit", [s["id"] for s in sublines],
                                format_func=lambda x: next(f"[{s['kode']}] {s['nama']}" for s in sublines if s["id"]==x))
    target_sub = next(s for s in sublines if s["id"] == pilih_sub_id)

    with st.form("form_edit_subline"):
        es1, es2 = st.columns(2)
        ed_kode = es1.text_input("Kode Subline", value=target_sub["kode"])
        ed_nama = es2.text_input("Nama Subline", value=target_sub["nama"])
        ed_ket = st.text_area("Keterangan", value=target_sub["keterangan"] or "")
        ed_aktif = st.checkbox("Status Aktif", value=bool(target_sub["aktif"]))
        simpan_es = st.form_submit_button("Simpan Perubahan Subline")

    if simpan_es:
        try:
            db.edit_subline(pilih_sub_id, ed_kode, ed_nama, ed_ket, ed_aktif, aktor=user["nama_pengguna"])
            st.success(f"Subline '{ed_nama}' berhasil diperbarui.")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal memperbarui: {e}")


def hal_seluruh_data():
    """4. Seluruh Data Lintas Admin & Subline: Pencarian & Filter Terpusat."""
    kop("Seluruh Data Operasional Sistem",
        "Pencarian dan monitoring seluruh data (paket, kontrak, anggaran, risiko) lintas admin tanpa pembatasan.",
        "SUPER ADMIN")

    f1, f2 = st.columns([5, 5])
    sublines = ["Semua Subline"] + [s["nama"] for s in db.daftar_subline()]
    filter_sbl = f1.selectbox("Filter Data Berdasarkan Subline", sublines, key="f_all_sub")
    cari_all = f2.text_input("🔍 Cari Data (Kata Kunci)", placeholder="Cari nama paket, kontrak, supplier, uraian...", key="f_all_txt")

    t1, t2, t3, t4, t5 = st.tabs(["📦 Paket Sasaran", "📑 Monitoring Kontrak", "💰 Posisi Anggaran", "🛡️ Risk Register", "⚖️ Log Keputusan"])

    is_filtered = (filter_sbl != "Semua Subline")

    with t1:
        pakets = db.rows("SELECT * FROM paket ORDER BY no")
        if is_filtered:
            pakets = [p for p in pakets if p.get("subline") == filter_sbl]
        if cari_all.strip():
            c = cari_all.strip().lower()
            pakets = [p for p in pakets if c in p["nama"].lower() or c in (p["kontrak"] or "").lower() or c in (p["catatan"] or "").lower()]

        st.dataframe(pd.DataFrame([{
            "No": p["no"], "Paket": p["nama"], "Subline": p.get("subline") or "-",
            "PPK / Admin": p["ppk"], "Pagu": rp(p["pagu"]), "Realisasi": rp(p["realisasi"]),
            "Capaian %": f"{id_num((p['realisasi']/p['target']*100) if p['target'] else 0)}%",
            "Kontrak": p["kontrak"] or "-", "Catatan": p["catatan"] or "-"
        } for p in pakets]), hide_index=True, width='stretch')

    with t2:
        kontraks = db.rows("SELECT * FROM kontrak ORDER BY id")
        if is_filtered:
            kontraks = [k for k in kontraks if k.get("subline") == filter_sbl]
        if cari_all.strip():
            c = cari_all.strip().lower()
            kontraks = [k for k in kontraks if c in k["nomor"].lower() or c in k["supplier"].lower() or c in k["uraian"].lower()]

        st.dataframe(pd.DataFrame([{
            "Nomor": k["nomor"], "Supplier": k["supplier"], "Subline": k.get("subline") or "-",
            "Nilai": rp(k["nilai"]), "Dibayar": rp(k["dibayar"]), "Sisa": rp(k["sisa"]),
            "Status": k["status"], "Selesai": k["selesai"]
        } for k in kontraks]), hide_index=True, width='stretch')

    with t3:
        anggaran = db.rows("SELECT * FROM anggaran ORDER BY periode DESC, kategori, id")
        st.dataframe(pd.DataFrame([{
            "Periode": a["periode"], "Kategori": a["kategori"], "Uraian": a["uraian"],
            "Pagu": rp(a["pagu"]), "Realisasi": rp(a["realisasi"]), "Sisa": rp(a["sisa"]),
            "Realisasi %": f"{id_num(a['persen'])}%", "Sumber": a["sumber"]
        } for a in anggaran]), hide_index=True, width='stretch')

    with t4:
        risiko = db.rows("SELECT * FROM risiko ORDER BY id")
        st.dataframe(pd.DataFrame([{
            "ID": r["id"], "Sasaran": r["sasaran"], "Risiko": r["risiko"],
            "Subline": r.get("subline") or "-", "Skor": (r["k"] or 0) * (r["d"] or 0),
            "Level": level_dari_skor((r["k"] or 0) * (r["d"] or 0)),
            "Mitigasi": r["mitigasi"], "PIC": r["pic"]
        } for r in risiko]), hide_index=True, width='stretch')

    with t5:
        keputusan = db.rows("SELECT * FROM keputusan ORDER BY id DESC")
        st.dataframe(pd.DataFrame([{
            "Waktu": k["waktu"], "Pengguna": k["pengguna"], "Objek": k["objek"],
            "Opsi": k["opsi"], "Dasar Pertimbangan": k["dasar"], "Tenggat": tgl_id(k["tenggat"])
        } for k in keputusan]), hide_index=True, width='stretch')


def hal_laporan_keseluruhan():
    """5. Laporan Keseluruhan & Arsip SATRIA."""
    kop("Laporan Keseluruhan & Arsip Dokumen",
        "Rekapitulasi eksekutif instrumen SATRIA Puslitbang Polri TA 2026 dan berkas resmi proyek perubahan.",
        "SUPER ADMIN")
    hal_ringkasan()


def hal_aktivitas_pengguna():
    """6. Aktivitas Pengguna Real-Time."""
    kop("Aktivitas Pengguna Real-Time",
        "Pemantauan langsung seluruh aktivitas admin dalam sistem (masuk, tambah data, ubah paket, ganti sandi).",
        "SUPER ADMIN")

    all_users = ["Semua Pengguna"] + [u["nama_pengguna"] for u in db.ambil_semua_pengguna()]
    f1, f2 = st.columns([4, 4])
    pilih_user = f1.selectbox("Filter Pengguna", all_users)
    pilih_aksi = f2.text_input("Filter Kata Kunci Aksi", placeholder="mis. Masuk, Perbarui, Tambah...")

    stream = db.ambil_audit_log(pengguna=pilih_user if pilih_user != "Semua Pengguna" else None,
                                aksi=pilih_aksi if pilih_aksi.strip() else None,
                                batas=60)
    if stream:
        st.dataframe(pd.DataFrame([{
            "Waktu": a["waktu"],
            "Pengguna": a["pengguna"],
            "Aksi": a["aksi"],
            "Detail Aktivitas": a["detail"]
        } for a in stream]), hide_index=True, width='stretch')
    else:
        st.info("Tidak ada aktivitas yang sesuai dengan filter.")


def hal_audit_log():
    """7. Audit Log Sistem."""
    kop("Audit Log Sistem",
        "Pencatatan jejak audit sistem yang tidak dapat diubah (immutable log).",
        "SUPER ADMIN")

    c1, c2, c3 = st.columns([4, 4, 3])
    cari_audit = c1.text_input("🔍 Pencarian Jejak Audit", placeholder="Cari dalam detail atau aksi...")
    semua_u = ["Semua Pengguna"] + [u["nama_pengguna"] for u in db.ambil_semua_pengguna()]
    filter_u = c2.selectbox("Pengguna", semua_u)
    batas_jml = c3.selectbox("Batas Baris", [50, 100, 200, 500], index=1)

    logs = db.ambil_audit_log(pengguna=filter_u if filter_u != "Semua Pengguna" else None,
                              cari=cari_audit,
                              batas=batas_jml)

    st.markdown(f"**Menampilkan {len(logs)} catatan audit terakhir:**")
    st.dataframe(pd.DataFrame([{
        "ID": l["id"],
        "Waktu": l["waktu"],
        "Pengguna": l["pengguna"],
        "Aksi": l["aksi"],
        "Detail": l["detail"]
    } for l in logs]), hide_index=True, width='stretch')


def hal_pengaturan_sistem():
    """8. Pengaturan Sistem Super Admin: Ambang Peringatan, Backup DB, & Keamanan."""
    kop("Pengaturan Sistem & Konfigurasi",
        "Pengaturan ambang peringatan dini, manajemen cadangan basis data, dan kata sandi Super Admin.",
        "SUPER ADMIN")
    hal_pengaturan()


# ------------------------------------------------------------------ FUNGSI HALAMAN ADMIN BIASA ----

def hal_admin_dashboard():
    """Dashboard Admin Pribadi (Terisolasi per Subline)."""
    sub = user.get("subline") or "PPK PUSLITBANG POLRI"
    kop(f"Selamat Datang, {user['nama']}",
        f"Ruang Kerja Terisolasi: {sub} — Peran: ADMIN | Status: AKTIF",
        sub)

    # Identitas Pengguna
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:16px 20px; box-shadow:0 3px 12px rgba(7,21,39,0.04); margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="font-size:0.78rem; font-weight:700; color:#64748b; text-transform:uppercase;">Identitas Akun Operasional</span>
                <div style="font-weight:800; font-size:1.15rem; color:#0d2342;">{user['nama']} ({user['nama_pengguna']})</div>
                <div style="color:#1d4ed8; font-size:0.84rem; font-weight:600; margin-top:2px;">🏢 {sub}</div>
            </div>
            <div>
                <span class='badge-aktif'>🟢 AKUN AKTIF</span>
                <span class='badge-subline'>ROLE: ADMIN</span>
                <div style="color:#94a3b8; font-size:0.72rem; margin-top:6px;">Terakhir Login: {user.get('terakhir_login', 'Sesi ini')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Statistik Khusus Subline Admin
    stt = db.ambil_statistik_subline(sub, is_super=False, paket_id=user.get("paket_id"))
    c = st.columns(4)
    c[0].metric("Pagu Paket Subline", rp(stt["total_pagu"]))
    c[1].metric("Realisasi Subline", rp(stt["total_realisasi"]), f"{id_num(stt['persen_capaian'])}% capaian")
    c[2].metric("Sisa Anggaran", rp(stt["total_pagu"] - stt["total_realisasi"]))
    c[3].metric("Paket Tanggung Jawab", stt["total_paket"])

    st.divider()

    # Tabel Paket Sasaran Milik Subline Admin
    st.subheader(f"📦 Paket Sasaran Milik {sub}")
    pakets_saya = db.ambil_paket_data(sub, is_super=False, paket_id=user.get("paket_id"))
    if pakets_saya:
        baris_p = []
        for p in pakets_saya:
            cap = (p["realisasi"] / p["target"] * 100) if p["target"] else 0
            lvl = "Hijau" if cap >= 80 else ("Kuning" if cap >= 50 else "Merah")
            baris_p.append({
                "No": p["no"],
                "Nama Paket": p["nama"],
                "Pagu": rp(p["pagu"]),
                "Target s.d. Bulan": rp(p["target"]),
                "Realisasi": rp(p["realisasi"]),
                "Capaian": f"{em(lvl)} {id_num(cap)}%",
                "Kontrak": p["kontrak"] or "-",
                "Catatan": p["catatan"] or "-"
            })
        st.dataframe(pd.DataFrame(baris_p), hide_index=True, width='stretch')
    else:
        st.info(f"Belum ada paket sasaran khusus yang dialokasikan pada Subline '{sub}'. Anda dapat memantau data operasional lainnya.")

    # Kontrak Subline
    kontraks_saya = db.ambil_kontrak_data(sub, is_super=False)
    if kontraks_saya:
        st.subheader(f"📑 Monitoring Kontrak {sub}")
        st.dataframe(pd.DataFrame([{
            "Nomor": k["nomor"],
            "Supplier": k["supplier"],
            "Nilai": rp(k["nilai"]),
            "Dibayar": rp(k["dibayar"]),
            "Sisa": rp(k["sisa"]),
            "Status": k["status"]
        } for k in kontraks_saya]), hide_index=True, width='stretch')

    # Keputusan KPA Terkait
    st.subheader("⚖️ Arahan & Keputusan KPA Terkait")
    ks = db.rows("SELECT * FROM keputusan ORDER BY id DESC LIMIT 5")
    if ks:
        st.dataframe(pd.DataFrame([{
            "Waktu": k["waktu"], "Objek": k["objek"], "Opsi": k["opsi"],
            "Dasar": k["dasar"], "Tenggat": tgl_id(k["tenggat"])
        } for k in ks]), hide_index=True, width='stretch')
    else:
        st.caption("Belum ada keputusan KPA tercatat.")


def hal_admin_profil():
    """8. Profil & Ganti Sandi Mandiri Admin."""
    kop("Profil & Pengaturan Akun", "Kelola kata sandi dan lihat rincian identitas subline Anda.")

    p1, p2 = st.columns([5, 5])
    with p1:
        st.subheader("👤 Informasi Akun")
        st.markdown(f"""
        - **Nama Lengkap:** {user['nama']}
        - **Nama Pengguna (Username):** `{user['nama_pengguna']}`
        - **Role:** ADMIN
        - **Subline Utama:** `{user.get('subline', '-')}` *(ditetapkan Super Admin)*
        - **Paket Tanggung Jawab:** `{user.get('paket_id') or '-'}`
        - **Status Akun:** 🟢 Aktif
        - **Terakhir Login:** {user.get('terakhir_login') or 'Sesi saat ini'}
        - **Waktu Dibuat:** {user.get('created_at') or '-'}
        """)
        st.info("ℹ️ Identitas subline ditetapkan secara terpusat oleh Super Admin dan tidak dapat diubah sendiri.")

    with p2:
        st.subheader("🔑 Ganti Kata Sandi Mandiri")
        with st.form("form_ganti_sandi_mandiri"):
            sandi_lama = st.text_input("Kata sandi saat ini", type="password")
            sandi_baru = st.text_input("Kata sandi baru (minimal 8 karakter)", type="password")
            sandi_ulang = st.text_input("Ulangi kata sandi baru", type="password")
            btn_ubah = st.form_submit_button("Perbarui Kata Sandi")

        if btn_ubah:
            if not db.verifikasi_login(user["nama_pengguna"], sandi_lama):
                st.error("Kata sandi saat ini tidak cocok.")
            elif len(sandi_baru) < 8:
                st.error("Kata sandi baru minimal 8 karakter.")
            elif sandi_baru != sandi_ulang:
                st.error("Ketikan kata sandi baru tidak sama.")
            else:
                db.ganti_sandi(user["nama_pengguna"], sandi_baru)
                st.success("Kata sandi berhasil diperbarui!")


# ------------------------------------------------------------------ HALAMAN OPERASIONAL LAMA (TERPELIHARA) ----

def hal_ringkasan():
    st.markdown('<meta http-equiv="refresh" content="%d">' % AUTO_REFRESH_DETIK, unsafe_allow_html=True)
    _t = db.one("SELECT periode FROM anggaran WHERE kategori='AGREGAT' ORDER BY id DESC LIMIT 1")
    _posisi = ((("Posisi data: laporan realisasi %s, " % _t["periode"]) if (_t and _t["periode"]) else "Posisi data: "))
    kop("📊 Ringkasan Pengendalian — KPA",
        _posisi + "monitoring kontrak OM-SPAN, IKPA s.d. Juli 2026, kartu kendali, risk register.",
        "PUSLITBANG POLRI")
    stempel_data()

    agg = [a for a in db.rows("SELECT * FROM anggaran WHERE kategori='AGREGAT' ORDER BY id DESC")]
    ikpa = db.rows("SELECT * FROM ikpa ORDER BY urutan")
    peringatan = db.daftar_peringatan()

    c = st.columns(5)
    if agg:
        a = agg[0]
        c[0].metric("Pagu TA 2026 (%s)" % a["periode"], rp(a["pagu"]))
        c[1].metric("Realisasi", rp(a["realisasi"]), "%s%% dari pagu" % id_num(a["persen"]))
        c[2].metric("Sisa anggaran", rp(a["sisa"]))
    if ikpa:
        terakhir = ikpa[-1]
        delta = terakhir["nilai"] - ikpa[-2]["nilai"] if len(ikpa) > 1 else 0.0
        c[3].metric("IKPA %s" % terakhir["bulan"], id_num(terakhir["nilai"]),
                    delta="%.2f poin vs bulan sebelum" % delta if delta else None)
    n_merah = sum(1 for p in peringatan if p["level"] == "Merah")
    n_kuning = sum(1 for p in peringatan if p["level"] == "Kuning")
    c[4].metric("Peringatan dini", "%d merah / %d kuning" % (n_merah, n_kuning))

    st.subheader("🚨 Peringatan dini (aturan ambang dapat diubah KPA)")
    if peringatan:
        dfp = pd.DataFrame([{"Level": "%s %s" % (em(p["level"]), p["level"]),
                             "Objek": p["objek"], "Peringatan": p["pesan"]}
                            for p in peringatan])
        st.dataframe(dfp, hide_index=True, width='stretch')
    else:
        st.success("Tidak ada peringatan dini pada posisi data saat ini.")

    st.subheader("Tren IKPA & capaian paket")
    k1, k2 = st.columns(2)
    with k1:
        if ikpa:
            dfi = pd.DataFrame(ikpa)[["bulan", "nilai"]].set_index("bulan")
            st.caption("Nilai IKPA Februari - Juli 2026 (sumber: screenshot SPAN, terverifikasi 3 Oktober 2026)")
            st.line_chart(dfi, height=260)
    with k2:
        pakets = db.rows("SELECT * FROM paket ORDER BY no")
        if pakets:
            data = []
            for p in pakets:
                cap = p["realisasi"] / p["target"] * 100 if p["target"] else 0
                data.append({"Paket": "%d. %s" % (p["no"], p["nama"][:34]), "Capaian %": cap})
            st.caption("Capaian realisasi terhadap target s.d. bulan (Kartu Kendali Juli 2026)")
            st.bar_chart(pd.DataFrame(data).set_index("Paket"), height=260)

    st.subheader("📅 Milestone proyek perubahan")
    ms = db.rows("SELECT * FROM milestone ORDER BY tanggal")
    hari_ini = date.today()
    kolom = st.columns(len(ms) if ms else 1)
    for i, m in enumerate(ms):
        t = datetime.strptime(m["tanggal"], "%Y-%m-%d").date()
        sisa = (t - hari_ini).days
        with kolom[i]:
            selesai = m["status"] == "Terlaksana"
            ikon = "🟢" if selesai else ("🔴" if sisa < 0 else ("🟡" if sisa <= 3 else "🔵"))
            st.markdown("**%s %s**" % (ikon, m["kode"]))
            st.caption("%s" % tgl_id(m["tanggal"]))
            st.write(m["nama"])
            if selesai:
                st.caption("Status: Terlaksana")
            elif sisa < 0:
                st.error("Terlambat %d hari" % (-sisa))
            else:
                st.caption("H-%d | status %s" % (sisa, m["status"]))

    st.subheader("🛡️ Profil risiko (Risk Register)")
    rr = db.rows("SELECT * FROM risiko ORDER BY id")
    if rr:
        ringkas = []
        for r in rr:
            skor = (r["k"] or 0) * (r["d"] or 0)
            ringkas.append({"ID": r["id"], "Risiko": r["risiko"][:60],
                            "Skor": skor, "Level": "%s %s" % (em(level_dari_skor(skor)), level_dari_skor(skor))})
        st.dataframe(pd.DataFrame(ringkas), hide_index=True, width='stretch')


def hal_anggaran():
    sub_filter = user.get("subline") if not is_sa else None
    kop("💰 Anggaran & Paket Sasaran",
        "Sumber: Realisasi Anggaran Puslitbang Polri + Kartu Kendali KPA Juli 2026.",
        sub_filter)

    st.subheader("Posisi anggaran menurut periode dan kategori")
    ang = db.ambil_anggaran_data(sub_filter, is_super=is_sa)
    dfa = pd.DataFrame([{
        "Periode": a["periode"], "Kategori": a["kategori"], "Uraian": a["uraian"],
        "Pagu (Rp)": rp(a["pagu"]), "Realisasi (Rp)": rp(a["realisasi"]),
        "Sisa (Rp)": rp(a["sisa"]), "Realisasi %": id_num(a["persen"]),
    } for a in ang])
    st.dataframe(dfa, hide_index=True, width='stretch')

    st.subheader("6 paket sasaran (Kartu Kendali KPA Juli 2026)")
    pakets = db.rows("SELECT * FROM paket ORDER BY no")
    baris = []
    for p in pakets:
        cap = p["realisasi"] / p["target"] * 100 if p["target"] else 0
        warna = db.float_setelan("capaian_merah", 50)
        kuning = db.float_setelan("capaian_kuning", 80)
        lvl = "Merah" if cap < warna else ("Kuning" if cap < kuning else "Hijau")
        milik_saya = boleh_ubah_paket(p["no"], user)
        baris.append({
            "No": p["no"], "Paket": p["nama"], "Subline": p.get("subline") or "-",
            "PPK": p["ppk"], "Pagu (Rp)": rp(p["pagu"]), "Target s.d. bln (Rp)": rp(p["target"]),
            "Realisasi (Rp)": rp(p["realisasi"]), "Capaian %": id_num(cap),
            "Capaian": "%s %s" % (em(lvl), lvl),
            "Tanggung Jawab": "⭐ Unit Anda" if milik_saya else "-",
            "Kontrak": p["kontrak"] or "-", "Catatan": p["catatan"] or "-",
        })
    st.dataframe(pd.DataFrame(baris), hide_index=True, width='stretch')

    st.subheader("✏️ Pembaruan data paket")
    if not pakets:
        st.warning("Belum ada data paket yang dialokasikan.")
        return

    pilihan_pkt = {("%d. %s" % (p["no"], p["nama"])): p for p in pakets}
    pilih = st.selectbox("Paket yang akan diperbarui", list(pilihan_pkt.keys()), key="pilih_paket_edit")
    target_pilih = pilihan_pkt[pilih]

    # Validasi backend: memeriksa izin kepemilikan paket
    izin = boleh_ubah_paket(target_pilih["no"], user)
    simpan = False
    if not izin:
        st.warning("Peran Admin hanya dapat mengubah paket yang menjadi tanggung jawabnya "
                   "(paket %s). Paket terpilih: %d." % (user.get("paket_id") or "-", target_pilih["no"]))

    with st.form("form_paket"):
        k2, k3 = st.columns([3, 3])
        if izin:
            nilai = k2.number_input("Realisasi terbaru (Rp)",
                                    value=int(target_pilih["realisasi"]),
                                    step=1000000, format="%d",
                                    key="nilai_paket_%d" % target_pilih["no"])
            catatan = k3.text_area("Catatan/status (termasuk hasil verifikasi)",
                                   value=target_pilih["catatan"] or "", height=100,
                                   key="catatan_paket_%d" % target_pilih["no"])
            simpan = st.form_submit_button("Simpan perubahan")
        else:
            st.form_submit_button("Simpan", disabled=True)

    if simpan and izin:
        db.run("UPDATE paket SET realisasi=?, catatan=?, diperbarui=? WHERE no=?",
               (int(nilai), catatan, datetime.now().strftime("%Y-%m-%d %H:%M"), target_pilih["no"]))
        db.audit(user["nama_pengguna"], "Perbarui paket %d" % target_pilih["no"],
                 "realisasi %s; catatan %s" % (rp(nilai), (catatan or "-")[:120]))
        st.success("Tersimpan. Perubahan tercatat pada audit.")
        st.rerun()


def hal_risiko():
    sub_filter = user.get("subline") if not is_sa else None
    kop("🛡️ Manajemen Risiko (Risk Register Kinerja)",
        "Skala 1-5, skor = Kemungkinan x Dampak. Ambang merah dilaporkan ke KPA 1x24 jam.",
        sub_filter)

    merah = db.float_setelan("risiko_merah", 10)
    kuning = db.float_setelan("risiko_kuning", 5)
    st.info("Ambang saat ini: Hijau 1-%d | Kuning %d-%d | Merah %d-25" % (kuning - 1, kuning, merah - 1, merah))

    rr = db.rows("SELECT * FROM risiko ORDER BY id")
    dfr = pd.DataFrame([{
        "ID": r["id"], "Sasaran/proses": r["sasaran"], "Risiko & penyebab": r["risiko"],
        "Dampak": r["dampak"], "Pengendalian": r["pengendalian"],
        "K": r["k"], "D": r["d"], "Skor": (r["k"] or 0) * (r["d"] or 0),
        "Level": "%s %s" % (em(level_dari_skor((r["k"] or 0) * (r["d"] or 0))), level_dari_skor((r["k"] or 0) * (r["d"] or 0))),
        "Mitigasi / PIC / tenggat": "%s / %s / %s" % (r["mitigasi"], r["pic"], r["tenggat"]),
        "Status & bukti": r["status"],
    } for r in rr])
    st.dataframe(dfr, hide_index=True, width='stretch')

    st.subheader("Matriks penilaian 5 x 5 (posisi risiko)")
    isi = {}
    for r in rr:
        isi.setdefault((r["d"], r["k"]), []).append(r["id"])
    grid = []
    for k in (5, 4, 3, 2, 1):
        baris = {"Kemungkinan %d" % k: ""}
        for d in (1, 2, 3, 4, 5):
            skor = k * d
            isi_risiko = ", ".join(isi.get((d, k), []))
            tanda = "%s skor %d %s" % (em(level_dari_skor(skor)), skor, isi_risiko)
            baris["Dampak %d" % d] = tanda
        grid.append(baris)
    st.dataframe(pd.DataFrame(grid), hide_index=True, width='stretch')

    if is_sa or user["nama_pengguna"] in ("pokja", "kpa"):
        st.subheader("✏️ Penilaian ulang / pembaruan risiko")
        if rr:
            pilih = st.selectbox("Risiko yang dinilai ulang", [r["id"] for r in rr], key="pilih_risiko_edit")
            r_now = next(r for r in rr if r["id"] == pilih)
            with st.form("form_risiko"):
                k2, k3, k4 = st.columns([1, 1, 6])
                kk = k2.number_input("Kemungkinan (1-5)", min_value=1, max_value=5, value=int(r_now["k"]), step=1, key="k_" + pilih)
                dd = k3.number_input("Dampak (1-5)", min_value=1, max_value=5, value=int(r_now["d"]), step=1, key="d_" + pilih)
                status = k4.text_area("Status/bukti (diperbarui)", value=r_now["status"] or "", height=100, key="st_" + pilih)
                simpan = st.form_submit_button("Simpan penilaian")
            if simpan:
                skor = int(kk) * int(dd)
                db.run("UPDATE risiko SET k=?, d=?, status=?, diperbarui=? WHERE id=?",
                       (int(kk), int(dd), status, datetime.now().strftime("%Y-%m-%d %H:%M"), pilih))
                db.audit(user["nama_pengguna"], "Perbarui risiko %s" % pilih,
                         "K=%d D=%d skor=%d level=%s" % (int(kk), int(dd), skor, level_dari_skor(skor)))
                st.success("Risiko %s diperbarui: skor %d (%s)." % (pilih, skor, level_dari_skor(skor)))
                st.rerun()


def hal_kontrak():
    sub_filter = user.get("subline") if not is_sa else None
    kop("📑 Monitoring Kontrak OM-SPAN",
        "Sumber: Ekspor Monitoring Data Kontrak OM-SPAN, satker 642377/KPPN 088.",
        sub_filter)

    ks = db.ambil_kontrak_data(sub_filter, is_super=is_sa)
    if not ks:
        st.warning("Belum ada data kontrak untuk lingkup ini.")
        return

    c = st.columns(4)
    c[0].metric("Jumlah kontrak", len(ks))
    c[1].metric("Total nilai kontrak", rp(sum(k["nilai"] for k in ks)))
    c[2].metric("Sudah dibayar", rp(sum(k["dibayar"] for k in ks)))
    c[3].metric("Terlambat termin", sum(1 for k in ks if "TERLAMBAT" in (k["status"] or "").upper()))

    dfk = pd.DataFrame([{
        "Nomor kontrak": k["nomor"], "Supplier": k["supplier"],
        "Tgl kontrak": k["tanggal_kontrak"], "Selesai": k["selesai"],
        "Uraian": k["uraian"], "Nilai (Rp)": rp(k["nilai"]),
        "Dibayar (Rp)": rp(k["dibayar"]), "Sisa (Rp)": rp(k["sisa"]),
        "Status": ("🔴 " + k["status"] if "TERLAMBAT" in (k["status"] or "").upper() else k["status"]),
        "Paket": k["paket_no"] or "-",
    } for k in ks])
    st.dataframe(dfk, hide_index=True, width='stretch')


def hal_milestone():
    kop("📅 Milestone & Kelengkapan Lampiran",
        "Milestone Proyek Perubahan PKN Tk. II dan status checklist kelengkapan L-01 s.d. L-15.")

    hari_ini = date.today()
    ms = db.rows("SELECT * FROM milestone ORDER BY tanggal")

    def label_sisa(m):
        if m["status"] == "Terlaksana":
            return "selesai"
        n = (datetime.strptime(m["tanggal"], "%Y-%m-%d").date() - hari_ini).days
        if n < 0:
            return "lewat %d hari" % (-n)
        return "hari ini" if n == 0 else "H-%d" % n

    dfm = pd.DataFrame([{
        "Kode": m["kode"], "Milestone": m["nama"], "Tanggal": tgl_id(m["tanggal"]),
        "Sisa waktu": label_sisa(m), "Status": m["status"],
        "Hasil/temuan": m["hasil"], "Eviden": m["eviden"],
    } for m in ms])
    st.dataframe(dfm, hide_index=True, width='stretch')

    st.subheader("📄 Dokumen 3 Pilar Output & Matriks Alur")
    _ada = False
    _kol = st.columns(2)
    for _i, _nama in enumerate(DOKUMEN_PILAR):
        _jalur = os.path.join(PILAR_DIR, _nama)
        if not os.path.exists(_jalur):
            continue
        _ada = True
        with open(_jalur, "rb") as _fh:
            _kol[_i % 2].download_button(
                "Unduh: " + _nama.split(" - ")[0], _fh.read(), file_name=_nama,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_pilar_" + _nama[:10])
    if _ada:
        st.caption("Folder dokumen: %s" % PILAR_DIR)
    else:
        st.info("Dokumen 3 Pilar Output belum ditemukan pada folder yang diharapkan.")

    if is_sa or user["nama_pengguna"] in ("kpa", "pokja"):
        st.subheader("✏️ Pembaruan milestone")
        pilih = st.selectbox("Milestone yang diperbarui", ["%s - %s" % (m["kode"], m["nama"]) for m in ms], key="pilih_ms_edit")
        m_now = next(m for m in ms if pilih.startswith(m["kode"] + " "))
        daftar_status = ["Terjadwal", "Dijalankan", "Terlaksana", "Tertunda"]
        status = st.selectbox("Status", daftar_status,
                              index=(daftar_status.index(m_now["status"]) if m_now["status"] in daftar_status else 0),
                              key="status_" + m_now["kode"])
        with st.form("form_milestone"):
            k3, k4 = st.columns([6, 6])
            hasil = k3.text_area("Hasil/temuan", value=m_now["hasil"] or "", height=100, key="hasil_" + m_now["kode"])
            eviden = k4.text_area("Eviden (nama file/lokasi)", value=m_now["eviden"] or "", height=100, key="eviden_" + m_now["kode"])
            simpan = st.form_submit_button("Simpan")
        if simpan:
            db.run("UPDATE milestone SET status=?, hasil=?, eviden=? WHERE kode=?", (status, hasil, eviden, m_now["kode"]))
            db.audit(user["nama_pengguna"], "Perbarui milestone %s" % m_now["kode"], "status %s" % status)
            st.success("Milestone %s diperbarui." % m_now["kode"])
            st.rerun()

    st.subheader("📋 Kelengkapan lampiran L-01 s.d. L-15")
    lampiran = db.status_lampiran()
    if lampiran:
        dfl = pd.DataFrame([{"Lampiran": l["kode"], "Judul": l["judul"], "Status": l["status"],
                             "[PERIKSA]": l["periksa"], "[ISI]": l["isi"]} for l in lampiran])
        st.dataframe(dfl, hide_index=True, width='stretch')
        n_selesai = sum(1 for l in lampiran if l["status"] == "Terisi")
        st.progress(n_selesai / len(lampiran),
                    text="Kelengkapan: %d dari %d bagian lampiran berstatus Terisi" % (n_selesai, len(lampiran)))
    else:
        st.warning("File checklist lampiran tidak ditemukan.")


def hal_keputusan():
    kop("⚖️ Keputusan & Arah KPA",
        "Ruang pencatatan keputusan pengendalian. Hanya KPA / Super Admin yang menambah keputusan; seluruh admin melihat log.")

    rr = db.rows("SELECT * FROM risiko ORDER BY id")
    pakets = db.rows("SELECT * FROM paket ORDER BY no")
    ms = db.rows("SELECT * FROM milestone ORDER BY tanggal")

    objek = ["Umum / anggaran"]
    objek += ["Risiko %s" % r["id"] for r in rr]
    objek += ["Paket %d - %s" % (p["no"], p["nama"]) for p in pakets]
    objek += ["Milestone %s" % m["kode"] for m in ms]
    opsi = ["Lanjut sesuai rencana", "Percepatan pelaksanaan/termin", "Pendampingan atau teguran PPK",
            "Revisi target atau jadwal", "Realokasi/penyesuaian anggaran", "Verifikasi data terlebih dahulu",
            "Eskalasi ke atasan / bahan sidang LPP"]

    if is_sa or user["nama_pengguna"] == "kpa":
        with st.form("form_keputusan"):
            k1, k2 = st.columns([3, 3])
            pilih_objek = k1.selectbox("Objek keputusan", objek)
            pilih_opsi = k2.selectbox("Opsi keputusan", opsi)
            dasar = st.text_area("Dasar pertimbangan (angka/bukti yang mendasari)", height=120,
                                 placeholder="Contoh: capaian paket 5 45,50% - dorong penyelesaian termin.")
            k3, k4 = st.columns([3, 3])
            tenggat = k3.date_input("Tenggat pelaksanaan", value=date.today())
            tambah = st.form_submit_button("Catat keputusan")

        if tambah:
            if not dasar.strip():
                st.error("Dasar pertimbangan wajib diisi.")
            else:
                db.run("INSERT INTO keputusan(waktu,pengguna,objek,opsi,dasar,tenggat,subline,created_by) VALUES (?,?,?,?,?,?,?,?)",
                       (datetime.now().strftime("%Y-%m-%d %H:%M"), user["nama_pengguna"],
                        pilih_objek, pilih_opsi, dasar.strip(), tenggat.strftime("%Y-%m-%d"),
                        user.get("subline", "PUSLITBANG POLRI PUSAT"), user["nama_pengguna"]))
                db.audit(user["nama_pengguna"], "Catat keputusan", "%s | %s" % (pilih_objek, pilih_opsi))
                st.success("Keputusan berhasil tercatat.")
                st.rerun()
    else:
        st.info("Pencatatan keputusan baru dibatasi untuk KPA / Super Admin.")

    st.subheader("Log Keputusan KPA")
    ks = db.rows("SELECT * FROM keputusan ORDER BY id DESC")
    if ks:
        st.dataframe(pd.DataFrame([{
            "Waktu": k["waktu"], "Oleh": k["pengguna"], "Objek": k["objek"],
            "Opsi": k["opsi"], "Dasar": k["dasar"], "Tenggat": tgl_id(k["tenggat"]),
        } for k in ks]), hide_index=True, width='stretch')
    else:
        st.caption("Belum ada keputusan tercatat.")


def hal_impor():
    kop("📥 Impor Data Realisasi & Kontrak",
        "Unggah ekspor asli SAKTI (.xlsx/.pdf) atau OM-SPAN (.xlsx) dengan validasi otomatis.")

    tab1, tab2 = st.tabs(["Laporan realisasi anggaran", "Monitoring kontrak"])
    with tab1:
        unggah = st.file_uploader("File laporan realisasi (.xlsx / .pdf)", type=["xlsx", "pdf"], key="up_realisasi")
        if unggah:
            isi = unggah.getvalue()
            try:
                kandidat = impor.baca_realisasi(isi, unggah.name)
            except Exception as exc:
                st.error("File tidak dapat dibaca: %s" % exc)
                kandidat = []
            if not kandidat:
                st.warning("Tidak ditemukan baris JUMLAH SELURUHNYA/GRAND TOTAL pada berkas ini.")
            else:
                st.write("Kandidat terdeteksi:")
                for i, k in enumerate(kandidat):
                    st.write(f"{i + 1}. [{k['format']}] {k['detail'] or ''} - pagu {rp(k['pagu'])} | realisasi {rp(k['realisasi'])}")
                pilih = st.number_input("Pilih nomor kandidat", min_value=1, max_value=len(kandidat), value=1, step=1)
                kunci = kandidat[int(pilih) - 1]
                periode = st.text_input("Label periode", value=kunci["periode"] or "Juli 2026")
                ada = db.one("SELECT id FROM anggaran WHERE periode=? AND kategori='AGREGAT'", (periode,))
                ganti = st.checkbox("Ganti data periode yang sudah ada" if ada else "Tambahkan data periode baru", value=bool(ada))
                if st.button("Simpan ke basis data", key="btn_simpan_realisasi"):
                    if ada and not ganti:
                        st.error("Data periode sudah ada - centang persetujuan penggantian.")
                    elif not kunci["valid"]:
                        st.error("Kandidat tidak lolos validasi.")
                    else:
                        sumber = "%s %s oleh %s pada %s" % (kunci["format"], kunci["detail"] or "", user["nama_pengguna"], datetime.now().strftime("%d-%m-%Y %H:%M"))
                        subline_rekam = user.get("subline") or "Urusan Keuangan (Urkeu)"
                        db.run("INSERT INTO anggaran(periode,kategori,uraian,pagu,realisasi,sisa,persen,sumber,subline,created_by) VALUES (?,?,?,?,?,?,?,?,?,?) "
                               "ON CONFLICT(periode,kategori,uraian) DO UPDATE SET pagu=excluded.pagu, realisasi=excluded.realisasi, sisa=excluded.sisa, persen=excluded.persen, sumber=excluded.sumber, subline=excluded.subline",
                               (periode, "AGREGAT", "GRAND TOTAL ANGGARAN PUSLITBANG POLRI TA 2026", kunci["pagu"], kunci["realisasi"], kunci["sisa"], kunci["persen"], sumber, subline_rekam, user["nama_pengguna"]))
                        if kunci["jenis"]:
                            for r in kunci["jenis"]["rinci"]:
                                db.run("INSERT INTO anggaran(periode,kategori,uraian,pagu,realisasi,sisa,persen,sumber,subline,created_by) VALUES (?,?,?,?,?,?,?,?,?,?) "
                                       "ON CONFLICT(periode,kategori,uraian) DO UPDATE SET pagu=excluded.pagu, realisasi=excluded.realisasi, sisa=excluded.sisa, persen=excluded.persen, sumber=excluded.sumber",
                                       (periode, "JENIS", "Belanja %s" % r["jenis"].title(), r["pagu"], r["realisasi"], r["pagu"] - r["realisasi"], r["persen"], sumber, subline_rekam, user["nama_pengguna"]))
                        ringkas = "periode %s; pagu %s; realisasi %s" % (periode, rp(kunci["pagu"]), rp(kunci["realisasi"]))
                        db.simpan_file_impor("realisasi", kunci["format"], unggah.name, isi, periode, ringkas, user["nama_pengguna"])
                        db.audit(user["nama_pengguna"], "Impor realisasi %s" % periode, ringkas)
                        st.success("Tersimpan untuk periode %s." % periode)
                        st.rerun()

    with tab2:
        unggah_k = st.file_uploader("File monitoring kontrak (.xlsx)", type=["xlsx"], key="up_kontrak")
        if unggah_k:
            data_k, waktu_u, sheet_k = _baca_kontrak(unggah_k)
            if not data_k:
                st.warning("Tabel kontrak tidak ditemukan.")
            else:
                st.write(f"Sheet **{sheet_k}** | {waktu_u} | {len(data_k)} kontrak terbaca.")
                if st.button("Ganti tabel kontrak dengan data ini", key="btn_ganti_kontrak"):
                    db.run("DELETE FROM kontrak")
                    pakets = db.rows("SELECT no, kontrak, subline FROM paket")
                    subline_default = user.get("subline") or "PPK PUSLITBANG POLRI"
                    for d in data_k:
                        no_pkt = None
                        sub_pkt = subline_default
                        for p in pakets:
                            for nomor in (p["kontrak"] or "").split(";"):
                                nomor = nomor.strip()
                                if nomor and d["nomor"].startswith(nomor):
                                    no_pkt = p["no"]
                                    if p.get("subline"):
                                        sub_pkt = p["subline"]
                        db.run("INSERT INTO kontrak(nomor,supplier,tanggal_kontrak,mulai,selesai,uraian,nilai,dibayar,sisa,status,paket_no,sumber,subline,created_by) "
                               "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                               (d["nomor"], d["supplier"], d["tanggal_kontrak"], d["mulai"], d["selesai"], d["uraian"],
                                d["nilai"], d["dibayar"], d["sisa"], d["status"], no_pkt, "OM-SPAN %s" % waktu_u, sub_pkt, user["nama_pengguna"]))
                    db.simpan_file_impor("kontrak", "OM-SPAN", unggah_k.name, unggah_k.getvalue(), "",
                                         "%d kontrak; %s" % (len(data_k), waktu_u), user["nama_pengguna"])
                    db.audit(user["nama_pengguna"], "Impor kontrak", "%d kontrak" % len(data_k))
                    st.success(f"{len(data_k)} kontrak tersimpan.")
                    st.rerun()


def _baca_kontrak(uploaded):
    xls = pd.ExcelFile(uploaded)
    for nama_sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=nama_sheet, header=None)
        hdr = None
        for idx, row in df.iterrows():
            nilai = [str(v).strip().upper() for v in row.tolist() if not pd.isna(v)]
            if "NOMOR KONTRAK" in nilai:
                hdr = idx
                peta = {str(v).strip().upper(): pos for pos, v in enumerate(row.tolist()) if not pd.isna(v)}
                break
        if hdr is None:
            continue
        butuh = ["NOMOR KONTRAK", "TANGGAL KONTRAK", "NAMA SUPPLIER", "TANGGAL MULAI", "TANGGAL SELESAI",
                 "URAIAN KONTRAK", "NILAI KONTRAK", "NILAI PEMBAYARAN", "SISA KONTRAK", "STATUS PROGRESS KONTRAK"]
        if any(b not in peta for b in butuh):
            continue
        waktu_unduh = ""
        for _, row in df.iterrows():
            vals = [str(v) for v in row.tolist() if not pd.isna(v)]
            for j, v in enumerate(vals):
                if v.lower().startswith("waktu unduh") and j + 1 < len(vals):
                    waktu_unduh = " ".join(vals[j:j + 2])

        def sel(row, kolom):
            v = row.iloc[peta[kolom]]
            return "" if pd.isna(v) else (int(v) if isinstance(v, float) and float(v).is_integer() else str(v).strip())

        data = []
        for _, row in df.iloc[hdr + 1:].iterrows():
            nomor = sel(row, "NOMOR KONTRAK")
            if not nomor:
                continue
            nilai = int(float(sel(row, "NILAI KONTRAK") or 0))
            dibayar = int(float(sel(row, "NILAI PEMBAYARAN") or 0))
            sisa = int(float(sel(row, "SISA KONTRAK") or 0))
            data.append(dict(
                nomor=str(nomor), supplier=str(sel(row, "NAMA SUPPLIER")),
                tanggal_kontrak=str(sel(row, "TANGGAL KONTRAK")),
                mulai=str(sel(row, "TANGGAL MULAI")), selesai=str(sel(row, "TANGGAL SELESAI")),
                uraian=str(sel(row, "URAIAN KONTRAK")), nilai=nilai, dibayar=dibayar, sisa=sisa,
                status=str(sel(row, "STATUS PROGRESS KONTRAK")),
                selisih_ok=abs((nilai - dibayar) - sisa) <= 1
            ))
        if data:
            return data, waktu_unduh, nama_sheet
    return [], "", ""


def hal_pengaturan():
    st.subheader("Ambang peringatan dini")
    daftar = [("ikpa_merah", "IKPA merah di bawah", 0, 100),
              ("ikpa_kuning", "IKPA kuning di bawah", 0, 100),
              ("capaian_merah", "Capaian paket merah di bawah (%)", 0, 100),
              ("capaian_kuning", "Capaian paket kuning di bawah (%)", 0, 100),
              ("risiko_merah", "Risiko merah pada skor >=", 1, 25),
              ("risiko_kuning", "Risiko kuning pada skor >=", 1, 25)]
    with st.form("form_ambang"):
        cols = st.columns(3)
        nilai_baru = {}
        for i, (kunci, label, lo, hi) in enumerate(daftar):
            with cols[i % 3]:
                nilai_baru[kunci] = st.number_input(
                    label, min_value=float(lo), max_value=float(hi),
                    value=float(db.float_setelan(kunci, 0)), step=1.0,
                    key="amb_" + kunci)
        simpan = st.form_submit_button("Simpan ambang")
    if simpan:
        for kunci, label, _, _ in daftar:
            db.set_setelan(kunci, nilai_baru[kunci], label)
        db.audit(user["nama_pengguna"], "Ubah ambang peringatan",
                 "; ".join("%s=%s" % (k, id_num(nilai_baru[k], 0)) for k, _, _, _ in daftar))
        st.success("Ambang diperbarui - peringatan dihitung ulang.")
        st.rerun()

    st.subheader("Ganti Kata Sandi")
    with st.form("form_sandi"):
        k1, k2, k3 = st.columns(3)
        lama = k1.text_input("Kata sandi saat ini", type="password")
        baru = k2.text_input("Kata sandi baru", type="password")
        ulangi = k3.text_input("Ulangi kata sandi baru", type="password")
        ubah = st.form_submit_button("Ganti kata sandi")
    if ubah:
        if not db.verifikasi_login(user["nama_pengguna"], lama):
            st.error("Kata sandi saat ini salah.")
        elif len(baru) < 8:
            st.error("Kata sandi baru minimal 8 karakter.")
        elif baru != ulangi:
            st.error("Ketikan kata sandi baru tidak sama.")
        else:
            db.ganti_sandi(user["nama_pengguna"], baru)
            st.success("Kata sandi berhasil diganti.")

    st.subheader("Backup basis data")
    if st.button("💾 Salin basis data ke folder backup", key="btn_backup_db"):
        jalur = db.backup_database()
        st.success("Backup tersimpan: %s" % jalur)

    st.subheader("Jejak audit (50 aktivitas terakhir)")
    audits = db.rows("SELECT * FROM audit ORDER BY id DESC LIMIT 50")
    st.dataframe(pd.DataFrame([{"Waktu": a["waktu"], "Pengguna": a["pengguna"],
                                "Aksi": a["aksi"], "Detail": a["detail"]}
                               for a in audits]), hide_index=True, width='stretch')


# ------------------------------------------------------------------ ROUTING UTAMA & PROTEKSI SERVER-SIDE ----

MENU_SUPER_KHUSUS = {
    "Dashboard Utama",
    "Manajemen Admin",
    "Manajemen Subline",
    "Seluruh Data",
    "Laporan Keseluruhan",
    "Aktivitas Pengguna",
    "Audit Log",
    "Pengaturan Sistem",
    "Pengaturan & Audit",
}

# Proteksi Server-Side: Pastikan admin biasa tidak dapat mengakses menu Super Admin
if pilihan in MENU_SUPER_KHUSUS and not is_sa:
    st.error("⛔ AKSES DITOLAK: Halaman ini hanya dapat diakses oleh SUPER ADMIN utama.")
    db.audit(user["nama_pengguna"], "Pelanggaran Akses Ditolak", f"Mencoba membuka halaman {pilihan}")
    st.stop()

PAGES = {
    # Menu Khusus Super Admin
    "Dashboard Utama": hal_super_dashboard,
    "Manajemen Admin": hal_manajemen_admin,
    "Manajemen Subline": hal_manajemen_subline,
    "Seluruh Data": hal_seluruh_data,
    "Laporan Keseluruhan": hal_laporan_keseluruhan,
    "Aktivitas Pengguna": hal_aktivitas_pengguna,
    "Audit Log": hal_audit_log,
    "Pengaturan Sistem": hal_pengaturan_sistem,
    # Menu Khusus Admin Biasa
    "Dashboard Admin": hal_admin_dashboard,
    "Profil & Akun": hal_admin_profil,
    # Menu Operasional Terintegrasi
    "Ringkasan KPA": hal_ringkasan,
    "Anggaran & Paket": hal_anggaran,
    "Manajemen Risiko": hal_risiko,
    "Kontrak": hal_kontrak,
    "Milestone & Lampiran": hal_milestone,
    "Keputusan KPA": hal_keputusan,
    "Impor Data (SAKTI/OM-SPAN)": hal_impor,
    "Pengaturan & Audit": hal_pengaturan,
}

if pilihan in PAGES:
    PAGES[pilihan]()
else:
    st.error(f"Halaman '{pilihan}' tidak ditemukan.")

kaki()
