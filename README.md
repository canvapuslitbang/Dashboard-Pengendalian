# SATRIA Dashboard — Pengendalian & Pengambilan Keputusan

Aplikasi lokal (LAN) pendukung **Proyek Perubahan PKN Tk. II "STRATEGI AKSELERASI TRANSFORMASI TATA KELOLA KEUANGAN BERBASIS RISIKO MELALUI SATRIA PUSLITBANG"** (Perpol 15/2024 jo. LKPP 4/2024 jo. 12/2021). Dipakai oleh KPA, PPK, Pokja, dan Urkeu untuk memantau paket sasaran, risiko, kontrak, milestone, dan lampiran L-01 s.d. L-15, serta mencatat keputusan KPA secara terdokumentasi.

> Menggunakan **Streamlit**, berjalan **offline/LAN tanpa internet**. Seluruh data tersimpan di basis data lokal `data\satria.db` (SQLite, mode WAL untuk baca-tulis bersamaan). Setiap perubahan data tercatat pada tabel audit. Aset visual (logo Puslitbang Polri, emblem SATRIA, latar gedung) disimpan lokal di `assets\` — aplikasi tetap berjalan walaupun aset dihapus.

---

## 1. Kebutuhan & Instalasi

| Perangkat | Keterangan |
|---|---|
| Python | 3.12 (terpasang: `C:\Users\sanga\AppData\Local\Programs\Python\Python312\python.exe`) |
| Paket | `streamlit`, `pandas`, `openpyxl`, **`pdfplumber`** (untuk impor PDF SAKTI) — lihat `requirements.txt` |

Instalasi paket (sekali saja):

```
C:\Users\sanga\AppData\Local\Programs\Python\Python312\python.exe -m pip install -r requirements.txt
```

## 2. Cara Menjalankan & Akses dari HP

**Cara termudah:** klik dua kali `jalankan.bat`, lalu buka `http://localhost:8501`.

**Lewat perintah:**

```
cd "E:\1. Dari_Laptop_Pribadi_22062021\15. PKN II WILHELMUS SANGA SE MM\2. PKN II th 2026\6. Proyek Perubahan PKN II 2026\6. Dashboard Pengendalian SATRIA"
C:\Users\sanga\AppData\Local\Programs\Python\Python312\python.exe -m streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

**Akses dari HP (Wi-Fi/LAN kantor):**

1. Laptop server dan HP harus **satu jaringan** (Wi-Fi/LAN kantor). Cari IP laptop server: `ipconfig` (mis. `172.16.101.131`).
2. **Sekali saja, izinkan port 8501 di firewall Windows** (sudah dibuat; buat ulang dari PowerShell administrator bila perlu):
   ```
   netsh advfirewall firewall add rule name="SATRIA 8501" dir=in action=allow protocol=TCP localport=8501 remoteip=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10 profile=any
   ```
   Aturan dibatasi hanya pada jaringan kantor (LAN) dan Tailscale — koneksi dari internet publik ditolak.
3. Di browser HP buka `http://<IP-laptop-server>:8501` → *Add to Home Screen* agar tampil seperti aplikasi.
4. **Data baru otomatis terlihat di HP** setiap kali Urkeu mengimpor — halaman Ringkasan memuat ulang otomatis tiap ±60 detik dan menampilkan stempel waktu pembaruan.

**Akses dari luar kantor (Tailscale):**

1. **Server laptop**: pastikan Tailscale terpasang dan sudah *Log in* (klik ikon Tailscale di system tray → *Log in*; gunakan akun Google/Microsoft/email apa pun).
2. **HP**: pasang aplikasi **Tailscale** dari Play Store / App Store, lalu masuk dengan **akun yang sama** → kedua perangkat otomatis berada dalam satu jaringan pribadi terenkripsi (WireGuard).
3. Dari HP di mana pun (4G/Wi-Fi luar kantor), buka `http://<alamat-100.x.x.x-laptop>:8501` — alamat dapat dicek di laptop dengan `tailscale ip -4` (mis. `http://100.87.12.34:8501`).
4. Syarat: laptop server **menyala, aplikasi SATRIA berjalan, dan laptop punya koneksi internet**; Tailscale menjaga lalu lintas tetap terenkripsi tanpa perlu membuka port di router kantor.

> **Keamanan akses:** dashboard hanya menerima koneksi dari LAN kantor dan tailnet Tailscale (bukan internet publik). Kata sandi bawaan **wajib diganti** tiap pengguna pada menu *Pengaturan & Audit* (khusus KPA) — untuk PPK/Pokja/Urkeu, ganti melalui KPA atau sesuaikan `db.py` lalu seed ulang. Database tetap lokal di laptop; Tailscale hanya membawa lalu lintas aplikasi yang terenkripsi.

## 3. Akun Bawaan & Arsitektur Peran (kata sandi: `satria2026`)

Sistem SATRIA menerapkan arsitektur **Single Super Admin & Multi-Admin Terisolasi** (Peran: `SUPER ADMIN` dan `ADMIN`):

| Akun | Peran | Subline / Unit Kerja | Hak Akses & Lingkup |
|---|---|---|---|
| `kpa` | **SUPER ADMIN** | PUSLITBANG POLRI PUSAT | **Satu-satunya Super Admin & Pemilik Sistem**: Akses seluruh data, manajemen admin, manajemen subline, audit global, konfigurasi sistem |
| `kristo` | **ADMIN** | PPK PUSLITBANG POLRI | Admin PPK Pengendalian (Paket 2 & 3, pemeliharaan gedung & fungsional) |
| `budi` | **ADMIN** | SUBLINE UNIT 02 | Admin Operasional Subline Unit 02 |
| `andi` | **ADMIN** | SUBLINE UNIT 03 | Admin Operasional Subline Unit 03 |
| `urkeu` | **ADMIN** | Urusan Keuangan (Urkeu) | Admin Keuangan: Impor realisasi SAKTI/OM-SPAN & rekonsiliasi |
| `pokja` | **ADMIN** | Pokja Data & Instrumen | Admin Instrumen: Pembaruan risiko & milestone |
| `ppk1` | **ADMIN** | Laboratorium Litbangyasa | Admin PPK Paket 1 (Peralatan Uji Laboratorium) |
| `ppk2` | **ADMIN** | PPK PUSLITBANG POLRI | Admin PPK Paket 2 & 3 (Pemeliharaan Gedung & Fungsional) |
| `ppk3` | **ADMIN** | Jasa Keamanan & Kebersihan | Admin PPK Paket 4 (Jasa Keamanan & Kebersihan) |
| `ppk4` | **ADMIN** | SPBE & Website | Admin PPK Paket 5 (SPBE, Jaringan & Website) |
| `ppk5` | **ADMIN** | Rutin Kendaraan & Logistik | Admin PPK Paket 6 (Pemeliharaan Rutin Kendaraan R4/6/10) |

> **Ketentuan Keamanan:**
> - Hanya boleh ada **SATU akun Super Admin** (`kpa`). Sistem memvalidasi ketat agar tidak dapat membuat Super Admin kedua.
> - Admin biasa dapat dibuat sebanyak yang dibutuhkan oleh Super Admin.
> - Data antaradmin terisolasi secara server-side berdasarkan Subline masing-masing.

## 4. Navigasi Menu Berdasarkan Role

### Menu SUPER ADMIN:
- **Dashboard Utama**: Ringkasan eksekutif, statistik subline, metrik aplikasi, grafik capaian, dan aktivitas terbaru.
- **Manajemen Admin**: Tabel admin (Tambah, Edit, Detail statistik per admin, Reset Sandi, Aktif/Nonaktif, Hapus).
- **Manajemen Subline**: Kelola unit kerja / subline (Tambah, Edit, Toggle Aktif, Distribusi data).
- **Seluruh Data**: Akses terpusat ke semua paket, kontrak, anggaran, risiko, milestone lintas admin.
- **Laporan Keseluruhan**: Rekapitulasi instrumen SATRIA, matriks 5x5 risiko, dan unduh dokumen 3 Pilar Output.
- **Aktivitas Pengguna**: Pemantauan langsung riwayat aksi seluruh admin secara real-time.
- **Audit Log**: Jejak audit sistem global yang tidak dapat diubah (immutable audit trail).
- **Pengaturan Sistem**: Ambang peringatan dini (IKPA, Capaian %, Skor Risiko) dan backup basis data.
- *(Seluruh menu operasional lama tetap tersedia dan dapat diakses).*

### Menu ADMIN BIASA:
- **Dashboard Admin**: Tampilan personalisasi ("Selamat Datang, [NAMA] — [SUBLINE]"), metrik terisolasi subline, dan arahan KPA.
- **Anggaran & Paket**: Monitoring dan pembaruan paket yang menjadi tanggung jawab subline admin.
- **Manajemen Risiko**: Monitoring profil risiko unit kerja dan matriks 5x5.
- **Kontrak**: Monitoring kontrak OM-SPAN milik subline admin.
- **Milestone & Lampiran**: Progres milestone M1 s.d. M6 dan status checklist L-01 s.d. L-15.
- **Keputusan KPA**: Log arahan dan keputusan KPA.
- **Impor Data (SAKTI/OM-SPAN)**: Fasilitas impor realisasi dan kontrak mandiri subline.
- **Profil & Akun**: Identitas akun dan ganti kata sandi mandiri.

## 5. Alur Impor Data (Urkeu)

Menu **Impor Data (SAKTI/OM-SPAN)**.

**Realisasi anggaran — sumber dideteksi otomatis:**

- **SAKTI** (`Laporan Fa Detail (16 Segmen)` dst., **.xlsx atau .pdf**): baris **JUMLAH SELURUHNYA** — pagu, realisasi s.d. periode, sisa; rincian jenis belanja (pegawai/barang/modal) dari baris akun dan **dicocokkan dengan total** sebelum disimpan.
- **OM-SPAN** (`Realisasi Anggaran Puslitbang Polri ... .xlsx`): baris **GRAND TOTAL** seperti sebelumnya.

Validasi sama untuk semua sumber: *sisa = pagu − realisasi* dan *periode lalu + periode ini = realisasi s.d. periode*. File **PDF hasil scan (gambar) ditolak** dengan pesan jelas — minta ekspor dari SAKTI sebagai PDF teks atau Excel.

Langkah:
1. Unggah file → aplikasi menampilkan kandidat (format, periode terdeteksi, satker) + rincian jenis belanja.
2. Pilih kandidat, periksa label periode (terisi otomatis, mis. `Oktober 2026`), centang persetujuan bila periode sudah ada.
3. *Simpan ke basis data* → tersimpan baris **AGREGAT** + baris **JENIS** (jika lolos pembanding), **berkas asli ikut disimpan** di basis data, dan tercatat pada audit.
4. **Semua pengguna (termasuk dari HP)** langsung melihat data periode baru di Ringkasan/Anggaran, dan dapat **men-download kembali berkas impor terakhir** dari menu Impor tanpa menyimpan salinan sendiri.

**Kontrak:** unggah `Monitoring Data Kontrak_*.xlsx` → aplikasi membaca baris kontrak, memvalidasi `nilai − dibayar = sisa`, lalu *Ganti tabel kontrak dengan data ini* (berkas asli juga tersimpan).

## 6. Peringatan Dini (ambang dapat diubah KPA)

| Indikator | Kuning | Merah |
|---|---|---|
| IKPA | < 97 | < 95 |
| Capaian paket | < 80% | < 50% |
| Skor risiko (K×D) | ≥ 5 | ≥ 10 |

Risiko merah memicu catat **lapor KPA 1×24 jam** (Risk Register Kinerja).

## 7. Struktur Folder

```
6. Dashboard Pengendalian SATRIA\
├─ app.py               # aplikasi Streamlit (halaman & peran)
├─ db.py                # skema SQLite, seed data, format angka, peringatan, lampiran, berkas impor
├─ impor.py             # parser realisasi: SAKTI (.xlsx/.pdf) & OM-SPAN (.xlsx)
├─ assets\              # desain: logo Puslitbang & SATRIA terbaru, foto gedung, latar (offline-safe)
│  └─ kegiatan\         # GALERI: salin foto kegiatan/uji coba ke sini → otomatis tampil
├─ .streamlit\config.toml  # tema warna institusi (navy & emas)
├─ data\satria.db       # basis data (SQLite) — backup otomatis di data\backup\
├─ requirements.txt     # paket Python
├─ jalankan.bat         # peluncur server
├─ test_app.py          # uji otomatis: login + semua halaman semua peran
├─ test_alur.py         # uji otomatis: keputusan, paket, ambang, sandi, risiko, impor SAKTI/OM-SPAN
└─ test_multiadmin_system.py  # uji otomatis 15 skenario: single Super Admin, multi-admin, isolasi subline
```

Uji otomatis (berjalan offline, tanpa server):

```
C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe test_multiadmin_system.py
C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe test_app.py
C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe test_alur.py
```

Ketiganya menuntaskan dengan `TOTAL GAGAL: 0` dan **membersihkan sendiri** data hasil uji.

## 8. Catatan Data (per 3 Oktober 2026)

- **IKPA** (Feb–Jul 2026): 98,92 · 95,63 · 97,67 · 96,08 · 95,58 · 94,38 (sumber: Kartu Kendali/OM-SPAN).
- **Agregat s.d. Juli 2026**: pagu Rp333.636.862.000 / realisasi Rp286.218.428.959 (85,79%).
- **6 paket sasaran + 7 kontrak** (SPPB/09/III, SPPB/1–3 Maracipta, SPPB/30/II, SPPBJ/5, SPPBJ/6; dua kontrak terakhir **BELUM SELESAI TERLAMBAT TERMIN**).
- **Milestone**: M1 10 Sep · M2 22 Sep · M3 4 Okt · M4 16 Okt · M5 28 Okt · M6 9 Nov · Sidang LPP 10 Nov · Penutupan 12 Nov 2026.
- `[PERIKSA]`/`[VERIFIKASI]`/`[ISI]`/`[TETAPKAN]` dalam draf dokumen **sengaja dipertahankan** sampai angkanya terkonfirmasi dari sumber resmi — jangan isi dengan angka rekaan.

## 9. Desain Tampilan & Galeri Kegiatan

Tampilan dashboard memakai identitas:

- **Logo Puslitbang Polri** (kiri) dan **logo SATRIA terbaru** (kanan) pada kepala halaman (hero) dan sidebar.
- **Foto gedung Puslitbang Polri** sebagai latar hero halaman (dengan lapisan gradasi) dan sebagai foto utama di halaman Masuk.
- **Warna institusi**: navy/Polri dengan aksen emas, ditambah warna kategori (biru, teal, emas, merah, ungu) pada kartu indikator agar tampilan hidup.
- **Tiga instrumen SATRIA** (SOP, Risk Register, Kartu Kendali KPA) ditampilkan sebagai kartu di halaman Masuk.
- Header aplikasi: **SATRIA = Strategi Akselerasi Transformasi Kinerja Organisasi Berbasis Risiko**, semboyan *"Kepastian Regulasi, Kemudahan Eksekusi"*.

### Menambah foto kegiatan / uji coba

Salin (copy-paste) foto ke folder:

```
...\6. Dashboard Pengendalian SATRIA\assets\kegiatan\
```

- Format: `.jpg` `.jpeg` `.png` `.webp`.
- Dashboard menampilkan sampai 15 foto teratas pada bagian **Galeri Kegiatan & Uji Coba** di halaman **Masuk** dan **Ringkasan KPA** — tanpa mengubah program.
- Foto kegiatan yang sudah tersedia (14 berkas) berasal dari `Eviden\Foto eviden` (rapat tim efektif, konsultasi mentor/coach, menghadap Kapuslitbang, dan dokumentasi kegiatan 14 Okt 2026).
- **Nama berkas menjadi keterangan foto** (contoh: `Rapat Pokja SATRIA 12 Okt 2026.jpg`).
- Disarankan foto lanskap (melebar), lebar 1200–1600 piksel, ukuran < 1,5 MB per foto.

### Berkas desain di `assets\`

| Berkas | Fungsi |
|---|---|
| `satria_logo.png` | logo SATRIA terbaru (latar hitam dijadikan transparan) |
| `satria_favicon.png` | ikon tab browser |
| `puslitbang_logo.png` | logo Puslitbang Polri (transparan) |
| `satria_badge.png` | emblem SATRIA (cadangan) |
| `hero.jpg` | foto hero kepala halaman (versi ringan) |
| `gedung_band.jpg` | foto gedung Puslitbang (versi ringan) |
| `gedung_watermark.png` | latar samar halaman |
| `polri_icon.png`, `puslitbang_favicon.png`, `bg_hero.png` | aset pendukung (cadangan) |
| `kegiatan\` | folder galeri foto kegiatan/uji coba |

> Seluruh aset bersifat **lokal/offline**. Aplikasi tetap berjalan walaupun berkas aset dihapus (bagian gambar akan dikosongkan tanpa error).

## 10. Buku Panduan (Manual Book)

Panduan penggunaan lengkap (instalasi, peran & hak akses, panduan tiap halaman, alur impor, peringatan dini, galeri, backup, dan penyelesaian masalah) tersedia dalam satu berkas di folder aplikasi ini:

```
Buku Panduan (Manual Book) Dashboard SATRIA Puslitbang - 2026.docx   (untuk disunting)
Buku Panduan (Manual Book) Dashboard SATRIA Puslitbang - 2026.pdf    (siap cetak/bagikan)
```

Isi: 15 bab dan Lampiran A–D, antara lain panduan tiap halaman, alur impor data,
peringatan dini, galeri, backup, penyelesaian masalah, contoh kasus penggunaan (uji
fungsi), serta lembar daftar isian hasil uji. Buku ini sudah memuat **tangkapan layar
asli** aplikasi: Halaman Masuk dan delapan halaman menu (Gambar 6.2 serta Gambar 7.1–7.8).

> Catatan: bila tampilan aplikasi berubah, tangkapan layar pada buku perlu diperbarui.
> Caranya dapat direproduksi dengan menjalankan aplikasi lalu mengambil tangkapan layar
> tiap halaman.
