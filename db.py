# -*- coding: utf-8 -*-
"""Basis data lokal Dashboard Pengendalian SATRIA Puslitbang (SQLite).

Seluruh angka awal (seed) berasal dari dokumen sumber yang sudah diverifikasi:
- Kartu Kendali Bulanan KPA berbasis Risiko, Bulan Juli 2026  -> daftar 6 paket
- Monitoring Data Kontrak OM-SPAN unduh 28-09-2026 (7 kontrak) -> tabel kontrak
- Realisasi Anggaran Puslitbang Polri Juli 2026 06082026.xlsx -> anggaran agregat,
  per bagian, dan per jenis belanja (baris GRAND TOTAL & baris TOTAL per blok)
- Nilai IKPA Februari-Juli 2026 (screenshot SPAN, diverifikasi visual 3 Okt 2026)
- Risk Register Kinerja SATRIA Puslitbang (pembaruan 28 September 2026)
- Matriks Milestone-Output-Eviden + Master Jadwal PKN ANGK XXVI

Aturan aplikasi: setiap perubahan data wajib meninggalkan jejak audit.
"""

import hashlib
import os
import random
import shutil
import sqlite3
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
DB_PATH = os.path.join(DATA_DIR, "satria.db")

CHECKLIST_MD = (
    r"E:\1. Dari_Laptop_Pribadi_22062021\15. PKN II WILHELMUS SANGA SE MM"
    r"\2. PKN II th 2026\6. Proyek Perubahan PKN II 2026\2. LPP PKN II TH 2026"
    r"\Draf LPP dan Lampiran - 22 September 2026"
    r"\03. Checklist Isian Data - Kerangka Lampiran L-01 sd L-15.md"
)

KATA_SANDI_BAWAAN = "satria2026"


# ---------------------------------------------------------------- koneksi ----
def connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA journal_mode=WAL")
    except sqlite3.Error:
        pass
    return con


def rows(sql, params=()):
    with connect() as con:
        return [dict(r) for r in con.execute(sql, params).fetchall()]


def one(sql, params=()):
    with connect() as con:
        r = con.execute(sql, params).fetchone()
        return dict(r) if r else None


def run(sql, params=()):
    with connect() as con:
        con.execute(sql, params)
        con.commit()


# --------------------------------------------------------------- utilitas ----
def _hash(sandi, garam):
    return hashlib.sha256((garam + sandi).encode("utf-8")).hexdigest()


def audit(pengguna, aksi, detail=""):
    run(
        "INSERT INTO audit(waktu, pengguna, aksi, detail) VALUES (?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pengguna, aksi, detail),
    )


def setelan(kunci, default=None):
    r = one("SELECT nilai FROM pengaturan WHERE kunci=?", (kunci,))
    return r["nilai"] if r else default


def set_setelan(kunci, nilai, keterangan=""):
    run(
        "INSERT INTO pengaturan(kunci, nilai, keterangan) VALUES (?,?,?) "
        "ON CONFLICT(kunci) DO UPDATE SET nilai=excluded.nilai",
        (kunci, str(nilai), keterangan),
    )


def float_setelan(kunci, default):
    try:
        return float(setelan(kunci, default))
    except (TypeError, ValueError):
        return float(default)


# --------------------------------------------------------------- file impor ----
def simpan_file_impor(jenis, format_, nama_file, isi, periode, ringkasan, pengimpor):
    run(
        "INSERT INTO file_impor(jenis, format, nama_file, isi, periode, ringkasan, "
        "pengimpor, waktu) VALUES (?,?,?,?,?,?,?,?)",
        (jenis, format_, nama_file, sqlite3.Binary(isi), periode, ringkasan, pengimpor,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )


def file_impor_terakhir(jenis):
    return one(
        "SELECT id, jenis, format, nama_file, isi, periode, ringkasan, pengimpor, waktu "
        "FROM file_impor WHERE jenis=? ORDER BY id DESC LIMIT 1", (jenis,))


def daftar_file_impor(jenis):
    return rows(
        "SELECT id, jenis, format, nama_file, periode, ringkasan, pengimpor, waktu, "
        "length(isi) AS ukuran FROM file_impor WHERE jenis=? ORDER BY id DESC", (jenis,))


def _id(x, des=2):
    """Format angka gaya Indonesia (koma desimal)."""
    return ("{:." + str(des) + "f}").format(x).replace(".", ",")


def is_super_admin(pengguna):
    """Memeriksa apakah pengguna berkedudukan sebagai Super Admin (satu-satunya di sistem)."""
    if not pengguna:
        return False
    peran = str(pengguna.get("peran") or "").strip().upper()
    return peran in ("SUPER ADMIN", "SUPERADMIN", "KPA")


def ambil_super_admin():
    """Mengambil satu-satunya akun Super Admin utama."""
    for p in rows("SELECT * FROM pengguna"):
        if is_super_admin(p):
            return p
    return None


def catat_login_sukses(nama_pengguna):
    """Memperbarui stempel waktu terakhir login pengguna."""
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run("UPDATE pengguna SET terakhir_login=? WHERE nama_pengguna=?", (waktu, nama_pengguna))


def verifikasi_login(nama_pengguna, sandi):
    nama_clean = (nama_pengguna or "").strip()
    r = one("SELECT * FROM pengguna WHERE nama_pengguna=? AND aktif=1", (nama_clean,))
    if not r:
        return None
    if _hash(sandi, r["garam"]) == r["hash"]:
        catat_login_sukses(nama_clean)
        # Ambil kembali data terbaru setelah terakhir_login dicatat
        return one("SELECT * FROM pengguna WHERE nama_pengguna=?", (nama_clean,))
    return None


def ganti_sandi(nama_pengguna, sandi_baru):
    r = one("SELECT garam FROM pengguna WHERE nama_pengguna=?", (nama_pengguna,))
    if not r:
        return False
    garam = r["garam"]
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run(
        "UPDATE pengguna SET hash=?, updated_at=? WHERE nama_pengguna=?",
        (_hash(sandi_baru, garam), waktu, nama_pengguna),
    )
    audit(nama_pengguna, "Ganti kata sandi", "kata sandi pengguna diperbarui")
    return True


# ----------------------------------------------------- manajemen admin & subline ----
def ambil_semua_pengguna(filter_subline=None, filter_status=None, cari=None):
    """Mengambil daftar pengguna dengan filter subline, status, dan pencarian nama/username."""
    query = "SELECT * FROM pengguna WHERE 1=1"
    params = []
    if filter_subline and filter_subline != "Semua Subline":
        query += " AND subline=?"
        params.append(filter_subline)
    if filter_status is not None and filter_status != "Semua Status":
        status_val = 1 if filter_status == "Aktif" else 0
        query += " AND aktif=?"
        params.append(status_val)
    if cari and cari.strip():
        c = f"%{cari.strip()}%"
        query += " AND (nama_pengguna LIKE ? OR nama LIKE ? OR subline LIKE ?)"
        params.extend([c, c, c])
    query += " ORDER BY (CASE WHEN peran IN ('SUPER ADMIN','SUPERADMIN','kpa') THEN 0 ELSE 1 END), nama_pengguna ASC"
    return rows(query, params)


def ambil_pengguna(nama_pengguna):
    """Mengambil satu akun pengguna berdasarkan username."""
    return one("SELECT * FROM pengguna WHERE nama_pengguna=?", (nama_pengguna,))


def tambah_admin(nama_pengguna, nama, sandi, subline, peran="ADMIN", paket_id=None, aktor="sistem"):
    """Menambah akun admin baru dengan validasi ketat agar TIDAK BISA membuat Super Admin kedua."""
    nama_clean = (nama_pengguna or "").strip().lower()
    if not nama_clean:
        raise ValueError("Nama pengguna (username) tidak boleh kosong.")
    if len(nama_clean) < 3:
        raise ValueError("Nama pengguna minimal 3 karakter.")
    if not nama or not nama.strip():
        raise ValueError("Nama lengkap admin tidak boleh kosong.")
    if not sandi or len(sandi) < 6:
        raise ValueError("Kata sandi minimal 6 karakter.")
    if not subline or not subline.strip():
        raise ValueError("Subline unit kerja wajib ditentukan oleh Super Admin.")

    # Validasi Role: HANYA BOLEH ADMIN, DILARANG MEMBUAT SUPER ADMIN BARU
    peran_clean = str(peran or "ADMIN").strip().upper()
    if peran_clean in ("SUPER ADMIN", "SUPERADMIN", "KPA"):
        raise ValueError("Sistem hanya mengizinkan SATU akun Super Admin. Dilarang membuat Super Admin tambahan.")

    # Periksa ketersediaan username
    if ambil_pengguna(nama_clean):
        raise ValueError(f"Nama pengguna '{nama_clean}' sudah digunakan. Gunakan username lain.")

    garam = "satria" + nama_clean
    hash_sandi = _hash(sandi, garam)
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    run(
        "INSERT INTO pengguna(nama_pengguna, nama, peran, subline, paket_id, garam, hash, aktif, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,1,?,?)",
        (nama_clean, nama.strip(), "ADMIN", subline.strip(), paket_id, garam, hash_sandi, waktu, waktu)
    )
    audit(aktor, "Tambah akun admin", f"Username: {nama_clean}, Nama: {nama.strip()}, Subline: {subline.strip()}")
    return True


def edit_admin(nama_pengguna, nama, subline, aktif, sandi_baru=None, paket_id=None, peran="ADMIN", aktor="sistem"):
    """Mengedit profil akun admin, subline, status aktif, dan kata sandi."""
    target = ambil_pengguna(nama_pengguna)
    if not target:
        raise ValueError(f"Pengguna '{nama_pengguna}' tidak ditemukan.")

    peran_target_is_sa = is_super_admin(target)
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if peran_target_is_sa:
        # Super Admin tidak boleh diubah perannya menjadi admin dan tidak boleh dinonaktifkan
        peran_final = target["peran"]
        aktif_final = 1
        subline_final = subline.strip() if (subline and subline.strip()) else target.get("subline", "PUSLITBANG POLRI PUSAT")
    else:
        # Admin biasa TIDAK BOLEH dinaikkan menjadi Super Admin
        peran_req = str(peran or "ADMIN").strip().upper()
        if peran_req in ("SUPER ADMIN", "SUPERADMIN", "KPA"):
            raise ValueError("Sistem hanya mengizinkan SATU akun Super Admin. Dilarang menaikkan admin biasa menjadi Super Admin.")
        peran_final = "ADMIN"
        aktif_final = 1 if aktif else 0
        subline_final = subline.strip() if subline else target.get("subline", "")

    if sandi_baru and sandi_baru.strip():
        if len(sandi_baru.strip()) < 6:
            raise ValueError("Kata sandi baru minimal 6 karakter.")
        garam = target["garam"]
        hash_sandi = _hash(sandi_baru.strip(), garam)
        run(
            "UPDATE pengguna SET nama=?, subline=?, aktif=?, paket_id=?, peran=?, hash=?, updated_at=? WHERE nama_pengguna=?",
            (nama.strip(), subline_final, aktif_final, paket_id, peran_final, hash_sandi, waktu, nama_pengguna)
        )
        audit(aktor, "Edit akun admin & reset sandi", f"Akun {nama_pengguna} diubah; sandi diperbarui; subline {subline_final}")
    else:
        run(
            "UPDATE pengguna SET nama=?, subline=?, aktif=?, paket_id=?, peran=?, updated_at=? WHERE nama_pengguna=?",
            (nama.strip(), subline_final, aktif_final, paket_id, peran_final, waktu, nama_pengguna)
        )
        audit(aktor, "Edit akun admin", f"Akun {nama_pengguna} diubah; subline {subline_final}; status {'Aktif' if aktif_final else 'Nonaktif'}")

    return True


def hapus_admin(nama_pengguna, aktor="sistem"):
    """Menghapus akun admin. Super Admin dilarang dihapus."""
    target = ambil_pengguna(nama_pengguna)
    if not target:
        raise ValueError(f"Pengguna '{nama_pengguna}' tidak ditemukan.")
    if is_super_admin(target):
        raise ValueError("Akun Super Admin utama tidak dapat dihapus.")

    run("DELETE FROM pengguna WHERE nama_pengguna=?", (nama_pengguna,))
    audit(aktor, "Hapus akun admin", f"Akun {nama_pengguna} ({target['nama']}) dihapus dari sistem")
    return True


def toggle_status_admin(nama_pengguna, aktif, aktor="sistem"):
    """Mengaktifkan atau menonaktifkan akun admin."""
    target = ambil_pengguna(nama_pengguna)
    if not target:
        raise ValueError(f"Pengguna '{nama_pengguna}' tidak ditemukan.")
    if is_super_admin(target) and not aktif:
        raise ValueError("Akun Super Admin utama tidak dapat dinonaktifkan.")

    val = 1 if aktif else 0
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run("UPDATE pengguna SET aktif=?, updated_at=? WHERE nama_pengguna=?", (val, waktu, nama_pengguna))
    status_teks = "diaktifkan" if val else "dinonaktifkan"
    audit(aktor, f"Ubah status akun: {status_teks}", f"Akun {nama_pengguna} {status_teks}")
    return True


def reset_sandi_admin(nama_pengguna, sandi_baru, aktor="sistem"):
    """Mereset kata sandi admin oleh Super Admin."""
    target = ambil_pengguna(nama_pengguna)
    if not target:
        raise ValueError(f"Pengguna '{nama_pengguna}' tidak ditemukan.")
    if not sandi_baru or len(sandi_baru.strip()) < 6:
        raise ValueError("Kata sandi baru minimal 6 karakter.")

    garam = target["garam"]
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run("UPDATE pengguna SET hash=?, updated_at=? WHERE nama_pengguna=?",
        (_hash(sandi_baru.strip(), garam), waktu, nama_pengguna))
    audit(aktor, "Reset sandi admin", f"Kata sandi akun {nama_pengguna} direset oleh {aktor}")
    return True


def daftar_subline(hanya_aktif=False):
    """Daftar seluruh subline beserta jumlah admin dan data terkait."""
    sql = """
    SELECT s.*,
           (SELECT COUNT(*) FROM pengguna p WHERE p.subline = s.nama) AS total_admin,
           (SELECT COUNT(*) FROM paket pkt WHERE pkt.subline = s.nama) AS total_paket,
           (SELECT COUNT(*) FROM kontrak k WHERE k.subline = s.nama) AS total_kontrak
    FROM subline s
    """
    if hanya_aktif:
        sql += " WHERE s.aktif=1"
    sql += " ORDER BY s.id ASC"
    return rows(sql)


def ambil_subline(subline_id):
    """Mengambil data subline berdasarkan id."""
    return one("SELECT * FROM subline WHERE id=?", (subline_id,))


def tambah_subline(kode, nama, keterangan="", aktor="sistem"):
    """Menambah subline baru ke dalam sistem."""
    k = (kode or "").strip().upper()
    n = (nama or "").strip()
    if not k or not n:
        raise ValueError("Kode dan nama subline wajib diisi.")
    if one("SELECT id FROM subline WHERE nama=?", (n,)):
        raise ValueError(f"Subline dengan nama '{n}' sudah ada.")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run("INSERT INTO subline(kode, nama, keterangan, aktif, created_at) VALUES (?,?,?,1,?)",
        (k, n, (keterangan or "").strip(), waktu))
    audit(aktor, "Tambah subline", f"Kode: {k}, Nama: {n}")
    return True


def edit_subline(subline_id, kode, nama, keterangan="", aktif=1, aktor="sistem"):
    """Mengedit data subline."""
    sub = ambil_subline(subline_id)
    if not sub:
        raise ValueError("Subline tidak ditemukan.")
    k = (kode or "").strip().upper()
    n = (nama or "").strip()
    if not k or not n:
        raise ValueError("Kode dan nama subline wajib diisi.")
    cek = one("SELECT id FROM subline WHERE nama=? AND id!=?", (n, subline_id))
    if cek:
        raise ValueError(f"Subline dengan nama '{n}' sudah digunakan pada ID lain.")
    run("UPDATE subline SET kode=?, nama=?, keterangan=?, aktif=? WHERE id=?",
        (k, n, (keterangan or "").strip(), 1 if aktif else 0, subline_id))
    audit(aktor, "Edit subline", f"ID {subline_id}: Kode {k}, Nama {n}, Status {'Aktif' if aktif else 'Nonaktif'}")
    return True


def hapus_subline(subline_id, aktor="sistem"):
    """Menghapus subline bila tidak ada admin yang terikat."""
    sub = ambil_subline(subline_id)
    if not sub:
        raise ValueError("Subline tidak ditemukan.")
    ada_admin = one("SELECT COUNT(*) AS c FROM pengguna WHERE subline=?", (sub["nama"],))["c"]
    if ada_admin > 0:
        raise ValueError(f"Subline '{sub['nama']}' tidak dapat dihapus karena masih digunakan oleh {ada_admin} admin.")
    run("DELETE FROM subline WHERE id=?", (subline_id,))
    audit(aktor, "Hapus subline", f"Subline '{sub['nama']}' dihapus.")
    return True


def ambil_detail_admin(nama_pengguna):
    """Mengambil detail lengkap seorang admin: identitas, subline, statistik data, dan riwayat."""
    u = ambil_pengguna(nama_pengguna)
    if not u:
        return None
    sbl = u.get("subline") or ""
    paket = rows("SELECT * FROM paket WHERE subline=? OR created_by=?", (sbl, nama_pengguna))
    kontrak = rows("SELECT * FROM kontrak WHERE subline=? OR created_by=?", (sbl, nama_pengguna))
    anggaran = rows("SELECT * FROM anggaran WHERE subline=? OR created_by=?", (sbl, nama_pengguna))
    risiko = rows("SELECT * FROM risiko WHERE subline=? OR created_by=?", (sbl, nama_pengguna))
    aktivitas = rows("SELECT * FROM audit WHERE pengguna=? ORDER BY id DESC LIMIT 20", (nama_pengguna,))

    return {
        "user": u,
        "subline": sbl,
        "paket": paket,
        "kontrak": kontrak,
        "anggaran": anggaran,
        "risiko": risiko,
        "aktivitas": aktivitas,
        "total_pagu": sum(p["pagu"] or 0 for p in paket),
        "total_realisasi": sum(p["realisasi"] or 0 for p in paket),
        "total_kontrak": len(kontrak),
        "total_kontrak_nilai": sum(k["nilai"] or 0 for k in kontrak),
    }


def ambil_riwayat_aktivitas(pengguna=None, batas=50):
    """Mengambil stream aktivitas pengguna terbaru secara real-time."""
    if pengguna:
        return rows("SELECT * FROM audit WHERE pengguna=? ORDER BY id DESC LIMIT ?", (pengguna, batas))
    return rows("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (batas,))


def ambil_audit_log(pengguna=None, aksi=None, cari=None, batas=100):
    """Mengambil catatan audit log dengan filter terstruktur."""
    sql = "SELECT * FROM audit WHERE 1=1"
    params = []
    if pengguna and pengguna != "Semua Pengguna":
        sql += " AND pengguna=?"
        params.append(pengguna)
    if aksi and aksi != "Semua Aksi":
        sql += " AND aksi LIKE ?"
        params.append(f"%{aksi}%")
    if cari and cari.strip():
        c = f"%{cari.strip()}%"
        sql += " AND (pengguna LIKE ? OR aksi LIKE ? OR detail LIKE ?)"
        params.extend([c, c, c])
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(batas)
    return rows(sql, params)


# ----------------------------------------------------- query data terisolasi ----
def ambil_paket_data(subline=None, is_super=False, paket_id=None):
    """Mengambil data paket dengan isolasi per subline untuk admin biasa."""
    if is_super:
        return rows("SELECT * FROM paket ORDER BY no")
    if subline:
        # Jika admin punya paket_id spesifik (mis. '2,3')
        if paket_id:
            nomors = [x.strip() for x in str(paket_id).split(",") if x.strip().isdigit()]
            if nomors:
                placeholders = ",".join(["?"] * len(nomors))
                return rows(f"SELECT * FROM paket WHERE subline=? OR no IN ({placeholders}) ORDER BY no", [subline] + nomors)
        return rows("SELECT * FROM paket WHERE subline=? ORDER BY no", (subline,))
    return []


def ambil_kontrak_data(subline=None, is_super=False):
    """Mengambil data kontrak dengan isolasi per subline untuk admin biasa."""
    if is_super:
        return rows("SELECT * FROM kontrak ORDER BY id")
    if subline:
        return rows("SELECT * FROM kontrak WHERE subline=? ORDER BY id", (subline,))
    return []


def ambil_anggaran_data(subline=None, is_super=False):
    """Mengambil data anggaran dengan isolasi per subline untuk admin biasa."""
    if is_super:
        return rows("SELECT * FROM anggaran ORDER BY periode DESC, kategori, id")
    if subline:
        # Menampilkan anggaran subline miliknya atau data agregat pusat
        return rows("SELECT * FROM anggaran WHERE subline=? OR subline='PUSLITBANG POLRI PUSAT' OR subline IS NULL ORDER BY periode DESC, kategori, id", (subline,))
    return []


def ambil_risiko_data(subline=None, is_super=False):
    """Mengambil data risiko dengan isolasi per subline untuk admin biasa."""
    if is_super:
        return rows("SELECT * FROM risiko ORDER BY id")
    if subline:
        return rows("SELECT * FROM risiko WHERE subline=? OR pic LIKE ? ORDER BY id", (subline, f"%{subline}%"))
    return []


def ambil_statistik_subline(subline=None, is_super=False, paket_id=None):
    """Menghitung agregasi statistik berdasarkan hak akses data."""
    pakets = ambil_paket_data(subline, is_super, paket_id)
    kontraks = ambil_kontrak_data(subline, is_super)
    risikos = ambil_risiko_data(subline, is_super)
    
    total_pagu = sum(p["pagu"] or 0 for p in pakets)
    total_realisasi = sum(p["realisasi"] or 0 for p in pakets)
    persen_capaian = (total_realisasi / total_pagu * 100) if total_pagu > 0 else 0.0
    
    total_kontrak_nilai = sum(k["nilai"] or 0 for k in kontraks)
    total_kontrak_dibayar = sum(k["dibayar"] or 0 for k in kontraks)
    kontrak_terlambat = sum(1 for k in kontraks if "TERLAMBAT" in (k["status"] or "").upper())
    
    risiko_merah = 0
    risiko_kuning = 0
    r_merah_ambang = float_setelan("risiko_merah", 10)
    r_kuning_ambang = float_setelan("risiko_kuning", 5)
    for r in risikos:
        skor = (r["k"] or 0) * (r["d"] or 0)
        if skor >= r_merah_ambang:
            risiko_merah += 1
        elif skor >= r_kuning_ambang:
            risiko_kuning += 1
            
    return {
        "total_paket": len(pakets),
        "total_pagu": total_pagu,
        "total_realisasi": total_realisasi,
        "persen_capaian": persen_capaian,
        "total_kontrak": len(kontraks),
        "total_kontrak_nilai": total_kontrak_nilai,
        "total_kontrak_dibayar": total_kontrak_dibayar,
        "kontrak_terlambat": kontrak_terlambat,
        "total_risiko": len(risikos),
        "risiko_merah": risiko_merah,
        "risiko_kuning": risiko_kuning,
    }


def backup_database():
    stempel = datetime.now().strftime("%Y%m%d_%H%M%S")
    tujuan = os.path.join(DATA_DIR, "backup", "satria_%s.db" % stempel)
    os.makedirs(os.path.dirname(tujuan), exist_ok=True)
    shutil.copy2(DB_PATH, tujuan)
    audit("sistem", "Backup database", tujuan)
    return tujuan


# ------------------------------------------------------------- peringatan ----
def daftar_peringatan():
    """Gabungan aturan peringatan dini. Mengembalikan list dict(level, pesan, objek)."""
    hasil = []
    ikpa_merah = float_setelan("ikpa_merah", 95)
    ikpa_kuning = float_setelan("ikpa_kuning", 97)
    cap_merah = float_setelan("capaian_merah", 50)
    cap_kuning = float_setelan("capaian_kuning", 80)
    risiko_merah = float_setelan("risiko_merah", 10)

    ikpa = rows("SELECT * FROM ikpa ORDER BY urutan")
    if ikpa:
        terakhir = ikpa[-1]
        nilai = terakhir["nilai"]
        if nilai < ikpa_merah:
            turun = ikpa[0]["nilai"] - nilai
            hasil.append(
                dict(level="Merah", objek="IKPA",
                     pesan="IKPA %s = %s di bawah ambang merah %s (turun %s poin sejak %s) "
                           "- perlu tindak lanjut kebijakan mutu anggaran"
                           % (terakhir["bulan"], _id(nilai), _id(ikpa_merah, 0), _id(turun),
                              ikpa[0]["bulan"]))
            )
        elif nilai < ikpa_kuning:
            hasil.append(dict(level="Kuning", objek="IKPA",
                              pesan="IKPA %s = %s di bawah ambang kuning %s"
                                    % (terakhir["bulan"], _id(nilai), _id(ikpa_kuning, 0))))

    for p in rows("SELECT * FROM paket ORDER BY no"):
        if p["target"]:
            cap = p["realisasi"] / p["target"] * 100
            if cap < cap_merah:
                hasil.append(dict(level="Merah", objek="Paket %d" % p["no"],
                                  pesan="Paket %s (PPK %s): capaian %s%% terhadap target s.d. bulan "
                                        "di bawah ambang merah %s%%"
                                        % (p["nama"], p["ppk"], _id(cap), _id(cap_merah, 0))))
            elif cap < cap_kuning:
                hasil.append(dict(level="Kuning", objek="Paket %d" % p["no"],
                                  pesan="Paket %s (PPK %s): capaian %s%% - di bawah ambang kuning %s%%"
                                        % (p["nama"], p["ppk"], _id(cap), _id(cap_kuning, 0))))

    for k in rows("SELECT * FROM kontrak"):
        if "TERLAMBAT" in (k["status"] or "").upper():
            hasil.append(dict(level="Merah", objek="Kontrak",
                              pesan="%s (%s) status %s - nilai Rp%s"
                                    % (k["nomor"], k["supplier"], k["status"],
                                       format(int(k["nilai"]), ",d").replace(",", "."))))

    today = datetime.now().date()
    for m in rows("SELECT * FROM milestone ORDER BY tanggal"):
        t = datetime.strptime(m["tanggal"], "%Y-%m-%d").date()
        sisa = (t - today).days
        if m["status"] == "Terlaksana":
            continue
        if sisa < 0:
            hasil.append(dict(level="Merah", objek=m["kode"],
                              pesan="%s %s lewat jadwal (%d hari) - status %s"
                                    % (m["kode"], m["nama"], -sisa, m["status"])))
        elif sisa <= 3:
            hasil.append(dict(level="Kuning", objek=m["kode"],
                              pesan="%s %s %s (H-%d) - status %s"
                                    % (m["kode"], m["nama"],
                                       "besok" if sisa == 1 else ("hari ini" if sisa == 0 else "3 hari lagi"),
                                       sisa, m["status"])))

    for r in rows("SELECT * FROM risiko"):
        if (r["k"] or 0) * (r["d"] or 0) >= risiko_merah:
            hasil.append(dict(level="Merah", objek=r["id"],
                              pesan="Risiko %s skor %d (K%d x D%d) - wajib dilaporkan ke KPA 1 x 24 jam"
                                    % (r["id"], (r["k"] or 0) * (r["d"] or 0), r["k"], r["d"])))

    for p in rows("SELECT * FROM paket WHERE catatan LIKE '%[PERIKSA%'"):
        hasil.append(dict(level="Kuning", objek="Data paket %d" % p["no"],
                          pesan="Butir [PERIKSA] pada paket %s - perlu konfirmasi Urkeu/PPK" % p["nama"]))
    return hasil


# ------------------------------------------------------- status lampiran ----
def status_lampiran():
    """Membaca checklist .md dan menyimpulkan status tiap lampiran L-01..L-15."""
    if not os.path.exists(CHECKLIST_MD):
        return []
    with open(CHECKLIST_MD, encoding="utf-8") as fh:
        teks = fh.read()
    bagian = []
    for blok in teks.split("\n### ")[1:]:
        judul = blok.split("\n", 1)[0].strip()
        isi = blok.split("\n### ", 1)[0]
        if not judul[:3].startswith("L-"):
            continue
        kode = judul.split(".")[0].strip()
        isi = blok.split("\n### ", 1)[0]
        rendah = isi.lower()
        if "[TETAPKAN]" in isi or "[VERIFIKASI" in isi:
            status = "Perlu keputusan/verifikasi"
        elif "[PERIKSA" in isi:
            status = "Perlu verifikasi data"
        elif "[ISI" in isi:
            status = "Perlu diisi"
        elif ("perlu diisi" in rendah or "perlu dilengkapi" in rendah
              or "perlu ditetapkan" in rendah or "dapat diisikan" in rendah
              or "perlu diisi" in rendah):
            status = "Perlu diisi (prosa)"
        elif "selesai" in rendah or "sudah terisi" in rendah:
            status = "Terisi"
        else:
            status = "Perlu ditelaah"
        bagian.append(dict(kode=kode, judul=judul, status=status,
                           periksa=isi.count("[PERIKSA"), isi=isi.count("[ISI")))
    return bagian


# ------------------------------------------------------------------ seed ----
def _seed():
    garam_default = "satria"
    pengguna = [
        ("kpa", "Brigjen Pol Didi Hayamansyah, S.H., S.I.K., M.H. (Kapuslitbang Polri - KPA)", "kpa", None),
        ("urkeu", "Wilhelmus Sanga, S.E., M.M. (Kaurkeu - Bendahara/Urkeu)", "urkeu", None),
        ("pokja", "Pokja Data dan Instrumen SATRIA", "pokja", None),
        ("ppk1", "KBP Caterina (PPK Laboratorium)", "ppk", "1"),
        ("ppk2", "IPTU Kristo (PPK Gedung & Peralatan Fungsional)", "ppk", "2,3"),
        ("ppk3", "AKP Handono (PPK Jasa Keamanan & Kebersihan)", "ppk", "4"),
        ("ppk4", "AKBP Septi (PPK SPBE & Website)", "ppk", "5"),
        ("ppk5", "AKP Gustika (PPK Rutin Kendaraan & Peralatan)", "ppk", "6"),
    ]
    for nama, lengkap, peran, paket_id in pengguna:
        garam = garam_default + nama
        run("INSERT INTO pengguna(nama_pengguna, nama, peran, paket_id, garam, hash, aktif) "
            "VALUES (?,?,?,?,?,?,1)",
            (nama, lengkap, peran, paket_id, garam, _hash(KATA_SANDI_BAWAAN, garam)))

    paket = [
        (1, "Peralatan Uji Laboratorium Litbangyasa (3 paket)", 300000000000, 260356756687, 269911522000,
         "KBP Caterina", "SPPB/1/II/2026; SPPB/2/II/2026; SPPB/3/II/2026", "",
         "Kartu Kendali Juli 2026; OM-SPAN 28-09-2026"),
        (2, "Pemeliharaan Gedung Kantor", 1983405172, 1983405172, 1090872844,
         "IPTU Kristo", "SPPBJ/5/IV/2026", "",
         "Kartu Kendali Juli 2026; OM-SPAN 28-09-2026"),
        (3, "Pemeliharaan Peralatan Fungsional", 1964584050, 1964584050, 982292025,
         "IPTU Kristo", "SPPBJ/6/IV/2026", "",
         "Kartu Kendali Juli 2026; OM-SPAN 28-09-2026"),
        (4, "Jasa Keamanan dan Kebersihan", 855221000, 855221000, 427610500,
         "AKP Handono", "SPPB/09/III/2026", "",
         "Kartu Kendali Juli 2026; OM-SPAN 28-09-2026"),
        (5, "Pemeliharaan Software/Hardware SPBE dan Website", 895864000, 895864000, 407649000,
         "AKBP Septi", "SPPB/30/II/2026",
         "[PERIKSA] selisih pagu Rp895.864.000 vs nilai kontrak Rp748.140.000 (Rp147.724.000) "
         "- rekonsiliasi Urkeu/PPK",
         "Kartu Kendali Juli 2026; OM-SPAN 28-09-2026"),
        (6, "Pemeliharaan Kendaraan R4/6/10, R2/3 dan Peralatan Kantor", 732074000, 732074000, 289334820,
         "AKP Gustika (PPK Rutin)", "",
         "[PERIKSA] paket rutin tidak tercantum pada ekspor monitoring kontrak OM-SPAN 28-09-2026 "
         "- nomor dokumen & metode perlu konfirmasi PPK",
         "Kartu Kendali Juli 2026 (RKAKL Rev.2 2026: kendaraan R4/6/10 21 unit, R2/3 2 unit)"),
    ]
    for p in paket:
        run("INSERT INTO paket(no,nama,pagu,target,realisasi,ppk,kontrak,catatan,sumber) "
            "VALUES (?,?,?,?,?,?,?,?,?)", p)

    kontrak = [
        ("SPPB/09/III/2026/PPK-PUSLITBANG", "FAISAL NAMIRA ABADI", "25 Maret 2026", "25 Maret 2026",
         "31 Desember 2026", "PENGADAAN TENAGA JASA KEAMANAN DAN KEBERSIHAN PUSLITBANG POLRI T.A. 2026",
         855221000, 427610500, 427610500, "BELUM SELESAI", 4),
        ("SPPB/1/II/2026/PUSLITBANG", "MARACIPTA UTAMA", "10 Februari 2026", "10 Februari 2026",
         "08 Agustus 2026", "PENGADAAN PERALATAN UJI LABORATORIUM RISET MOBILE SATKER PUSLITBANG POLRI TAHUN ANGGARAN 2026",
         99751680000, 99751680000, 0, "SELESAI TEPAT WAKTU", 1),
        ("SPPB/2/II/2026/PUSLITBANG", "MARACIPTA UTAMA", "10 Februari 2026", "10 Februari 2026",
         "08 Agustus 2026", "PENGADAAN PERALATAN LABORATORIUM UJI TEST BENCH MOBILE SATKER PUSLITBANG POLRI T.A. 2026",
         99716800000, 99716800000, 0, "SELESAI TEPAT WAKTU", 1),
        ("SPPB/3/II/2026/PUSLITBANG", "MARACIPTA UTAMA", "10 Februari 2026", "10 Februari 2026",
         "08 Agustus 2026", "PENGADAAN PERALATAN LABORATORIUM UJI PENETRATION TESTING MOBILE SATKER PUSLITBANG POLRI",
         99749700000, 99749700000, 0, "SELESAI TEPAT WAKTU", 1),
        ("SPPB/30/II/2026/PPK-PUSLITBANG", "PT.SOLU FILANTROPI TEKNOLOGI", "13 Februari 2026",
         "13 Februari 2026", "31 Desember 2026",
         "PENGADAAN PEMELIHARAAN JARINGAN (SOFTWARE SPBE, HARDWARE SPBE DAN PEMELIHARAAN WEBSITE PUSLITBANG POLRI T.A. 2026",
         748140000, 374070000, 374070000, "BELUM SELESAI", 5),
        ("SPPBJ/5/IV/2026/PPK/PUSLITBANG", "GARATJIPTA LAUTAN BERLIAN", "02 April 2026", "02 April 2026",
         "08 Desember 2026", "PEMELIHARAAN GEDUNG KANTOR PUSLITBANG POLRI T.A. 2026",
         1983405172, 1090872844, 892532328, "BELUM SELESAI TERLAMBAT TERMIN", 2),
        ("SPPBJ/6/IV/2026/PPK/PUSLITBANG", "PRO SOLUSI INDONESIA", "10 April 2026", "10 April 2026",
         "06 Desember 2026", "PEMELIHARAAN PERALATAN FUNGSIONAL PUSLITBANG POLRI T.A. 2026",
         1964584050, 982292025, 982292025, "BELUM SELESAI TERLAMBAT TERMIN", 3),
    ]
    sql_kontrak = (
        "INSERT INTO kontrak(nomor,supplier,tanggal_kontrak,mulai,selesai,uraian,nilai,dibayar,"
        "sisa,status,paket_no,sumber) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)")
    for k in kontrak:
        run(sql_kontrak, k + ("OM-SPAN Monitoring Data Kontrak unduh 28-09-2026",))

    anggaran = [
        ("Juli 2026", "AGREGAT", "GRAND TOTAL ANGGARAN PUSLITBANG POLRI TA 2026",
         333636862000, 286218428959, 47418433041, 85.787411871473608,
         "Realisasi Anggaran Puslitbang Polri Juli 2026 06082026.xlsx, sheet 'Realisasi Juli sd 2026', baris GRAND TOTAL"),
        ("Juni 2026", "AGREGAT", "GRAND TOTAL ANGGARAN PUSLITBANG POLRI TA 2026",
         333720245000, 280440470703, 53279774297, 84.034599310269599,
         "Realisasi Anggaran Puslitbang Polri Juli 2026 06082026.xlsx, sheet 'Realisasi Juni sd 2026'"),
        ("Juli 2026", "BAGIAN", "Bagian Urkeu", 15167126000, 9208543386, 5958582614, 60.713831915156504,
         "xlsx sheet 'Realisasi Juli sd 2026', baris 'URKEU Bel Barang dan Pegawai TOTAL'"),
        ("Juni 2026", "BAGIAN", "Bagian Urkeu", 15214980000, 4870390370, 10344589630, 32.01049472296382,
         "xlsx sheet 'Realisasi Juni sd 2026', baris 'URKEU Bel Barang dan Pegawai TOTAL'"),
        ("Juli 2026", "JENIS", "Belanja Pegawai", 13039798000, 8312636161, 4727161839, 63.748197334038458,
         "xlsx sheet 'Realisasi Juli sd 2026', baris 'Gaji dan Tunjangan' (jumlah pagu 3 jenis = pagu GRAND TOTAL)"),
        ("Juli 2026", "JENIS", "Belanja Barang", 20597064000, 7994270798, 12602793202, 38.812311780247867,
         "LPP Bab III & xlsx (selisih pagu GRAND TOTAL - modal - pegawai)"),
        ("Juli 2026", "JENIS", "Belanja Modal", 300000000000, 269911522000, 30088478000, 89.97050733333333,
         "xlsx sheet 'Realisasi Juli sd 2026' & RKAKL (pagu modal Rp300.000.000.000)"),
    ]
    for a in anggaran:
        run("INSERT INTO anggaran(periode,kategori,uraian,pagu,realisasi,sisa,persen,sumber) "
            "VALUES (?,?,?,?,?,?,?,?)", a)

    ikpa = [("Februari 2026", 1, 98.92), ("Maret 2026", 2, 95.63), ("April 2026", 3, 97.67),
            ("Mei 2026", 4, 96.08), ("Juni 2026", 5, 95.58), ("Juli 2026", 6, 94.38)]
    for bulan, urutan, nilai in ikpa:
        run("INSERT INTO ikpa(bulan, urutan, nilai, sumber, verifikasi) VALUES (?,?,?,?,?)",
            (bulan, urutan, nilai, "Screenshot SPAN - file PDF Nilai IKPA %s" % bulan,
             "TERVERIFIKASI 3 Oktober 2026 (verifikasi visual penulis; citra 204x206 px tidak terbaca OCR)"))

    risiko = [
        ("R-01", "Pengadaan barang/jasa",
         "Perlambatan belanja barang: lelang terlambat, dokumen tidak siap",
         "Realisasi Semester I rendah; penumpukan akhir tahun", "SOP Kontraktual 2025",
         3, 4, "Percepatan Pra-DIPA, inventarisasi paket, checklist", "PPK", "Desember 2026",
         "Realisasi sd. Juli 2026 85,79%; monitoring kontrak OM-SPAN (7 kontrak terunggah)"),
        ("R-02", "Kesiapan dokumen pengadaan", "Keterlambatan KAK/spek teknis/HPS",
         "Paket tidak dapat dilelang", "Checklist manual", 2, 3,
         "Jadwal kesiapan dini; monitoring bulanan", "Unit/PPK", "November 2026",
         "Checklist kesiapan paket pengadaan dini TA 2027"),
        ("R-03", "Pelaksana (kultur kerja)", "Delaying habit/keraguan PPK memulai",
         "Penundaan tahapan pengadaan", "SOP kontraktual", 3, 3,
         "Pendampingan, contoh pengisian, Komitmen Kerja Bersama", "Project Leader", "Oktober 2026",
         "Pendampingan berjalan; 2 kontrak pemeliharaan terlambat termin"),
        ("R-04", "Pembayaran/SPJ", "Keterlambatan dokumen SPJ/spesifikasi",
         "Pembayaran tertunda; realisasi menumpuk", "Checklist PJ keuangan", 2, 3,
         "Rekonsiliasi berkala; pengingat tenggat", "Bendahara/BPP", "Bulanan",
         "Rekonsiliasi SP2D dengan KPPN berjalan"),
        ("R-05", "Kepemimpinan (KPA)", "Transisi/mutasi KPA, keputusan tertunda",
         "Business continuity terganggu", "Belum ada prosedur transisi", 2, 4,
         "SOP mitigasi transisi, berkas serah terima", "Sespuslitbang", "Saat transisi/mutasi",
         "SOP mitigasi transisi disusun (draf)"),
        ("R-06", "Perencanaan anggaran", "Perubahan kebijakan/revisi anggaran",
         "Penyesuaian rencana dan pagu", "RKAKL revisi", 2, 3,
         "Pemutakhiran daftar paket dan kartu", "Subbag REN", "Saat revisi diterbitkan",
         "Revisi DIPA ke-5 posting 16-09-2026"),
    ]
    for r in risiko:
        run("INSERT INTO risiko(id,sasaran,risiko,dampak,pengendalian,k,d,mitigasi,pic,tenggat,status) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)", r)

    milestone = [
        ("M1", "Pembentukan Tim Efektif", "2026-09-10", "Terlaksana",
         "Sprin Tim Efektif Sprin/1022/VIII/HUM.10.2/2026 (18 September 2026); Sprin terbit 18 September 2026 (sesuai A.8 Log Activity & Checklist PROPER)",
         "Surat Perintah Sprin TIM EFEKTIF.pdf; Sprin TIM POKJA.pdf"),
        ("M2", "Pembuatan output proyek perubahan", "2026-09-22", "Terlaksana",
         "3 output tersedia: SOP, Risk Register, Kartu Kendali (draf untuk ditelaah)",
         "Folder 3 Pilar Output SATRIA (3 dokumen .docx)"),
        ("M3", "Uji coba instrumen", "2026-10-04", "Dijalankan",
         "[ISI hasil uji coba - 4 Oktober 2026]", "[ISI bukti: foto, daftar hadir, form uji coba L-07B]"),
        ("M4", "Analisis evaluasi", "2026-10-16", "Terjadwal",
         "[ISI catatan hasil analisis evaluasi]", "[ISI bukti]"),
        ("M5", "Penetapan SATRIA sebagai inovasi", "2026-10-28", "Terjadwal",
         "[ISI dokumen penetapan (nomor SK, tanggal, pejabat pengesah)]", "[ISI bukti]"),
        ("M6", "Kembali ke Pusdikmin & sidang LPP", "2026-11-09", "Terjadwal",
         "[ISI catatan hasil] - sidang LPP 10 November 2026, penutupan 12 November 2026",
         "[ISI bukti]"),
    ]
    for m in milestone:
        run("INSERT INTO milestone(kode,nama,tanggal,status,hasil,eviden) VALUES (?,?,?,?,?,?)", m)

    setelan_awal = [
        ("ikpa_merah", 95, "IKPA di bawah nilai ini = merah"),
        ("ikpa_kuning", 97, "IKPA di bawah nilai ini = kuning"),
        ("capaian_merah", 50, "Capaian realisasi terhadap target s.d. bulan (%): di bawah ini = merah"),
        ("capaian_kuning", 80, "Capaian (%): di bawah ini = kuning"),
        ("risiko_merah", 10, "Skor risiko (KxD) di atas/sama dengan nilai ini = merah (eskalasi KPA 1x24 jam)"),
        ("risiko_kuning", 5, "Skor risiko: di atas/sama dengan nilai ini = kuning"),
    ]
    for k, v, ket in setelan_awal:
        set_setelan(k, v, ket)

    audit("sistem", "Inisialisasi database", "data awal dari dokumen sumber terverifikasi")


SKEMA = """
CREATE TABLE IF NOT EXISTS pengguna(
  nama_pengguna TEXT PRIMARY KEY, nama TEXT NOT NULL, peran TEXT NOT NULL,
  paket_id TEXT, garam TEXT NOT NULL, hash TEXT NOT NULL, aktif INTEGER DEFAULT 1,
  subline TEXT, terakhir_login TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS subline(
  id INTEGER PRIMARY KEY AUTOINCREMENT, kode TEXT UNIQUE, nama TEXT UNIQUE,
  keterangan TEXT, aktif INTEGER DEFAULT 1, created_at TEXT);
CREATE TABLE IF NOT EXISTS paket(
  no INTEGER PRIMARY KEY, nama TEXT, pagu INTEGER, target INTEGER, realisasi INTEGER,
  ppk TEXT, kontrak TEXT, catatan TEXT, sumber TEXT, diperbarui TEXT,
  subline TEXT, created_by TEXT);
CREATE TABLE IF NOT EXISTS kontrak(
  id INTEGER PRIMARY KEY AUTOINCREMENT, nomor TEXT UNIQUE, supplier TEXT,
  tanggal_kontrak TEXT, mulai TEXT, selesai TEXT, uraian TEXT,
  nilai INTEGER, dibayar INTEGER, sisa INTEGER, status TEXT,
  paket_no INTEGER, sumber TEXT,
  subline TEXT, created_by TEXT);
CREATE TABLE IF NOT EXISTS anggaran(
  id INTEGER PRIMARY KEY AUTOINCREMENT, periode TEXT, kategori TEXT, uraian TEXT,
  pagu INTEGER, realisasi INTEGER, sisa INTEGER, persen REAL, sumber TEXT,
  subline TEXT, created_by TEXT,
  UNIQUE(periode, kategori, uraian));
CREATE TABLE IF NOT EXISTS file_impor(
  id INTEGER PRIMARY KEY AUTOINCREMENT, jenis TEXT NOT NULL, format TEXT,
  nama_file TEXT NOT NULL, isi BLOB NOT NULL, periode TEXT,
  ringkasan TEXT, pengimpor TEXT, waktu TEXT,
  subline TEXT);
CREATE TABLE IF NOT EXISTS ikpa(
  bulan TEXT PRIMARY KEY, urutan INTEGER, nilai REAL, sumber TEXT, verifikasi TEXT);
CREATE TABLE IF NOT EXISTS risiko(
  id TEXT PRIMARY KEY, sasaran TEXT, risiko TEXT, dampak TEXT, pengendalian TEXT,
  k INTEGER, d INTEGER, mitigasi TEXT, pic TEXT, tenggat TEXT, status TEXT,
  diperbarui TEXT,
  subline TEXT, created_by TEXT);
CREATE TABLE IF NOT EXISTS milestone(
  kode TEXT PRIMARY KEY, nama TEXT, tanggal TEXT, status TEXT, hasil TEXT, eviden TEXT,
  subline TEXT, created_by TEXT);
CREATE TABLE IF NOT EXISTS keputusan(
  id INTEGER PRIMARY KEY AUTOINCREMENT, waktu TEXT, pengguna TEXT, objek TEXT,
  opsi TEXT, dasar TEXT, tenggat TEXT,
  subline TEXT, created_by TEXT);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT, waktu TEXT, pengguna TEXT, aksi TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS pengaturan(
  kunci TEXT PRIMARY KEY, nilai TEXT, keterangan TEXT);
"""


def migrasi_db():
    """Migrasi skema database multi-admin & subline secara aman tanpa merusak data lama."""
    kolom_tambahan = {
        "pengguna": [
            ("subline", "TEXT"),
            ("terakhir_login", "TEXT"),
            ("created_at", "TEXT"),
            ("updated_at", "TEXT"),
        ],
        "paket": [
            ("subline", "TEXT"),
            ("created_by", "TEXT"),
        ],
        "kontrak": [
            ("subline", "TEXT"),
            ("created_by", "TEXT"),
        ],
        "anggaran": [
            ("subline", "TEXT"),
            ("created_by", "TEXT"),
        ],
        "risiko": [
            ("subline", "TEXT"),
            ("created_by", "TEXT"),
        ],
        "milestone": [
            ("subline", "TEXT"),
            ("created_by", "TEXT"),
        ],
        "keputusan": [
            ("subline", "TEXT"),
            ("created_by", "TEXT"),
        ],
        "file_impor": [
            ("subline", "TEXT"),
        ],
    }
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS subline(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              kode TEXT UNIQUE,
              nama TEXT UNIQUE,
              keterangan TEXT,
              aktif INTEGER DEFAULT 1,
              created_at TEXT
            );
        """)
        for tabel, cols in kolom_tambahan.items():
            cur = con.execute("PRAGMA table_info(%s)" % tabel)
            existing = {r["name"] for r in cur.fetchall()}
            for col_name, col_type in cols:
                if col_name not in existing:
                    try:
                        con.execute("ALTER TABLE %s ADD COLUMN %s %s" % (tabel, col_name, col_type))
                    except Exception:
                        pass
        con.commit()

    sublines_bawaan = [
        ("PPK-PUSLITBANG", "PPK PUSLITBANG POLRI", "Pejabat Pembuat Komitmen Satker Puslitbang Polri"),
        ("SUBLINE-02", "SUBLINE UNIT 02", "Subline Unit Kerja 02 Puslitbang"),
        ("SUBLINE-03", "SUBLINE UNIT 03", "Subline Unit Kerja 03 Puslitbang"),
        ("LAB-YASA", "Laboratorium Litbangyasa", "Unit Laboratorium Litbangyasa Puslitbang Polri"),
        ("SPBE-WEB", "SPBE & Website", "Unit SPBE dan Portal Web Puslitbang Polri"),
        ("RUTIN-LOG", "Rutin Kendaraan & Logistik", "Unit Pemeliharaan Rutin Kendaraan & Logistik"),
        ("URKEU", "Urusan Keuangan (Urkeu)", "Urusan Keuangan & Perbendaharaan Satker Puslitbang Polri"),
        ("POKJA-DATA", "Pokja Data & Instrumen", "Kelompok Kerja Data dan Instrumen SATRIA"),
        ("JASA-K3", "Jasa Keamanan & Kebersihan", "Unit Pengadaan Tenaga Jasa Pengamanan & Kebersihan"),
    ]
    with connect() as con:
        for kode, nama, ket in sublines_bawaan:
            con.execute("""
                INSERT INTO subline(kode, nama, keterangan, aktif, created_at)
                VALUES (?, ?, ?, 1, datetime('now', 'localtime'))
                ON CONFLICT(nama) DO NOTHING
            """, (kode, nama, ket))
        con.commit()

    run("UPDATE pengguna SET peran='SUPER ADMIN', subline='PUSLITBANG POLRI PUSAT' WHERE nama_pengguna='kpa'")

    pemetaan_lama = {
        "urkeu": "Urusan Keuangan (Urkeu)",
        "pokja": "Pokja Data & Instrumen",
        "ppk1": "Laboratorium Litbangyasa",
        "ppk2": "PPK PUSLITBANG POLRI",
        "ppk3": "Jasa Keamanan & Kebersihan",
        "ppk4": "SPBE & Website",
        "ppk5": "Rutin Kendaraan & Logistik",
    }
    for u, s in pemetaan_lama.items():
        run("UPDATE pengguna SET subline=?, peran='ADMIN' WHERE nama_pengguna=?", (s, u))

    garam_default = "satria"
    users_contoh = [
        ("kristo", "KRISTO", "ADMIN", "PPK PUSLITBANG POLRI", "2,3"),
        ("budi", "BUDI SANTOSO", "ADMIN", "SUBLINE UNIT 02", None),
        ("andi", "ANDI PRATAMA", "ADMIN", "SUBLINE UNIT 03", None),
    ]
    for usr, nm, prn, sbl, pkt in users_contoh:
        if not one("SELECT nama_pengguna FROM pengguna WHERE nama_pengguna=?", (usr,)):
            g = garam_default + usr
            h = _hash(KATA_SANDI_BAWAAN, g)
            run("""INSERT INTO pengguna(nama_pengguna, nama, peran, subline, paket_id, garam, hash, aktif, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now', 'localtime'))""",
                (usr, nm, prn, sbl, pkt, g, h))

    paket_subline = {
        1: ("Laboratorium Litbangyasa", "ppk1"),
        2: ("PPK PUSLITBANG POLRI", "kristo"),
        3: ("PPK PUSLITBANG POLRI", "kristo"),
        4: ("Jasa Keamanan & Kebersihan", "ppk3"),
        5: ("SPBE & Website", "ppk4"),
        6: ("Rutin Kendaraan & Logistik", "ppk5"),
    }
    for no, (sbl, crt) in paket_subline.items():
        run("UPDATE paket SET subline=?, created_by=? WHERE no=?", (sbl, crt, no))
        run("UPDATE kontrak SET subline=?, created_by=? WHERE paket_no=?", (sbl, crt, no))

    run("UPDATE anggaran SET subline='Urusan Keuangan (Urkeu)', created_by='urkeu' WHERE subline IS NULL OR subline=''")
    run("UPDATE risiko SET subline='PPK PUSLITBANG POLRI', created_by='kristo' WHERE id IN ('R-01','R-02','R-03')")
    run("UPDATE risiko SET subline='Urusan Keuangan (Urkeu)', created_by='urkeu' WHERE id='R-04'")
    run("UPDATE risiko SET subline='PUSLITBANG POLRI PUSAT', created_by='kpa' WHERE id='R-05'")
    run("UPDATE risiko SET subline='Pokja Data & Instrumen', created_by='pokja' WHERE id='R-06'")
    run("UPDATE milestone SET subline='Pokja Data & Instrumen', created_by='pokja' WHERE subline IS NULL OR subline=''")
    run("UPDATE keputusan SET subline='PUSLITBANG POLRI PUSAT', created_by='kpa' WHERE subline IS NULL OR subline=''")


def init():
    os.makedirs(DATA_DIR, exist_ok=True)
    with connect() as con:
        con.executescript(SKEMA)
        con.commit()
    if one("SELECT COUNT(*) AS n FROM pengguna")["n"] == 0:
        _seed()
    migrasi_db()


if __name__ == "__main__":
    init()
    print("Database siap:", DB_PATH)
    print("Paket:", len(rows("SELECT * FROM paket")),
          "| Kontrak:", len(rows("SELECT * FROM kontrak")),
          "| Risiko:", len(rows("SELECT * FROM risiko")),
          "| Milestone:", len(rows("SELECT * FROM milestone")))
