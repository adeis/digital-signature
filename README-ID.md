# Digital Signature Manager

**🌐 Language:** [English](README.md) | **Bahasa Indonesia**

Aplikasi Python yang komprehensif untuk membuat dan mengelola tanda tangan digital menggunakan sertifikat X.509. Tool ini memungkinkan Anda untuk membuat Certificate Authority (CA), menghasilkan sertifikat pengguna, menandatangani dokumen, dan memverifikasi tanda tangan digital.

## Fitur

- 🔐 **Manajemen Root CA** - Buat dan kelola Certificate Authority Anda sendiri
- 👤 **Pembuatan Sertifikat Pengguna** - Buat sertifikat untuk pengguna berdasarkan alamat email
- ✍️ **Penandatanganan Dokumen** - Tandatangani dokumen PDF dan teks dengan tanda tangan digital
- ✅ **Verifikasi Tanda Tangan** - Verifikasi keaslian dokumen yang ditandatangani
- 🔍 **Pemeriksaan Integritas Dokumen** - Pastikan dokumen tidak diubah-ubah
- 📄 **Watermarking PDF** - Tambahkan watermark tanda tangan pada dokumen PDF yang ditandatangani
- 📊 **Manajemen Metadata** - Simpan dan ambil metadata tanda tangan dalam format JSON

## Konsep

### Apa itu Tanda Tangan Digital?

Tanda tangan digital adalah mekanisme kriptografi yang menyediakan:
- **Autentikasi** - Memverifikasi identitas penandatangan
- **Integritas** - Memastikan dokumen tidak dimodifikasi
- **Non-repudiasi** - Mencegah penandatangan menyangkal bahwa mereka menandatangani dokumen

### Komponen Utama

#### 1. Root Certificate Authority (Root CA)
**Root CA** adalah fondasi kepercayaan dalam sistem tanda tangan digital kita:
- Bertindak sebagai **pihak ketiga terpercaya** yang menerbitkan dan memvalidasi sertifikat
- Memiliki **sertifikat self-signed** (menandatangani sertifikatnya sendiri)
- Berisi **pasangan kunci publik-privat**:
  - **Kunci privat**: Digunakan untuk menandatangani sertifikat pengguna (dirahasiakan)
  - **Kunci publik**: Digunakan untuk memverifikasi sertifikat yang diterbitkan oleh CA ini
- **Periode validitas**: Biasanya 10 tahun (3650 hari)
- **Trust anchor**: Semua sertifikat dalam sistem memperoleh kepercayaan dari Root CA

#### 2. Sertifikat Pengguna (X.509)
Sertifikat pengguna adalah **kartu identitas digital** yang berisi:
- **Kunci publik** pengguna
- **Informasi identitas** (email, nama, organisasi)
- **Tanda tangan digital dari Root CA** (membuktikan keaslian)
- **Periode validitas** (biasanya 1 tahun)
- **Nomor seri** (pengenal unik)

**Rantai Kepercayaan Sertifikat:**
```
Root CA (self-signed) → Sertifikat Pengguna (ditandatangani oleh Root CA)
```

#### 3. Proses Tanda Tangan Digital

**📝 Alur Proses Penandatanganan:**
```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Dokumen    │───▶│  SHA-256    │───▶│  Hash Dokumen│
│  (asli)      │    │  Hashing    │    │   (256-bit)  │
└──────────────┘    └─────────────┘    └──────┬───────┘
                                              │
                    ┌─────────────┐          │
                    │ Kunci Privat│          │
                    │  Pengguna   │          │
                    │ (RSA 2048)  │          │
                    └──────┬──────┘          │
                           │                 │
                           ▼                 ▼
                    ┌─────────────────────────────┐
                    │     Enkripsi RSA            │
                    │   (PKCS#1 v1.5 Padding)    │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │    Tanda Tangan Digital     │
                    │      (file .sig)            │
                    └─────────────────────────────┘
```

**✅ Alur Proses Verifikasi:**
```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Dokumen    │───▶│  SHA-256    │───▶│ Hash Saat Ini│
│ (untuk       │    │  Hashing    │    │   (256-bit)  │
│  verifikasi) │    │             │    │              │
└──────────────┘    └─────────────┘    └──────┬───────┘
                                              │
┌──────────────┐    ┌─────────────┐          │
│ Tanda Tangan │───▶│ Kunci Publik│          │
│   Digital    │    │  Pengguna   │          │
│ (file .sig)  │    │(dari sert.) │          │
└──────────────┘    └──────┬──────┘          │
                           │                 │
                           ▼                 ▼
                    ┌─────────────────────────────┐
                    │     Dekripsi RSA            │
                    │   → Hash Asli               │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │    Perbandingan Hash        │
                    │ Hash Asli == Hash Saat Ini?│
                    │                             │
                    │ ✅ COCOK = AUTENTIK         │
                    │ ❌ TIDAK COCOK = DIUBAH     │
                    └─────────────────────────────┘
```

#### 4. Public Key Infrastructure (PKI)

**🏗️ Arsitektur PKI:**
```
                    ┌─────────────────────────────────┐
                    │         ROOT CA                 │
                    │    ┌─────────────────────┐      │
                    │    │   Kunci Privat      │      │ ← Self-signed
                    │    │   (rootca.key)      │      │   Trust Anchor
                    │    └─────────────────────┘      │
                    │    ┌─────────────────────┐      │
                    │    │ Sertifikat Publik   │      │
                    │    │   (rootca.crt)      │      │
                    │    └─────────────────────┘      │
                    └─────────────┬───────────────────┘
                                  │ menandatangani & menerbitkan
                                  ▼
        ┌─────────────────────────────────────────────────────────┐
        │               SERTIFIKAT PENGGUNA                       │
        │  ┌─────────────────┐    ┌─────────────────┐            │
        │  │ alice@email.crt │    │  bob@email.crt  │    ...     │
        │  │ alice@email.key │    │  bob@email.key  │            │
        │  └─────────────────┘    └─────────────────┘            │
        └─────────────┬───────────────────┬─────────────────────┘
                      │                   │
                      ▼                   ▼
        ┌─────────────────────┐  ┌─────────────────────┐
        │  ALICE MENANDATANGANI│  │   BOB MENANDATANGANI│
        │                     │  │                     │
        │ ┌─────────────────┐ │  │ ┌─────────────────┐ │
        │ │ kontrak.pdf     │ │  │ │ laporan.txt     │ │
        │ │ + tanda tangan  │ │  │ │ + tanda tangan  │ │
        │ └─────────────────┘ │  │ └─────────────────┘ │
        └─────────────────────┘  └─────────────────────┘
```

**🔄 Diagram Alur Kerja Lengkap:**
```
┌─────────────────────────────────────────────────────────────────┐
│                   ALUR KERJA TANDA TANGAN DIGITAL              │
└─────────────────────────────────────────────────────────────────┘

1️⃣ FASE SETUP
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Buat      │───▶│   Buat      │───▶│   Siap      │
│  Root CA    │    │ Sert. User  │    │ Tandatangan │
└─────────────┘    └─────────────┘    └─────────────┘

2️⃣ FASE PENANDATANGANAN
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Dokumen    │───▶│   Hash      │───▶│   Enkripsi  │───▶│ Tanda Tangan│
│   Asli      │    │ (SHA-256)   │    │ dgn Kunci   │    │  Terbuat    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

3️⃣ FASE VERIFIKASI
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Dokumen    │───▶│   Hash      │───▶│ Bandingkan  │───▶│   Hasil     │
│+ Tanda Tangan│   │ + Dekripsi  │    │   Hash      │    │ ✅ atau ❌  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

4️⃣ STRUKTUR FILE
certificates/
├── alice@email.crt  ┐
├── alice@email.key  ├─ Identitas Pengguna
├── bob@email.crt    │
└── bob@email.key    ┘

signatures/
├── kontrak_alice.sig        ┐
├── signed_kontrak_alice.pdf ├─ Dokumen Tertandatangani
├── metadata_kontrak_alice.json ┘
├── laporan_bob.sig          ┐
├── signed_laporan_bob.pdf   ├─ Dokumen Tertandatangani  
└── metadata_laporan_bob.json ┘

rootca.crt  ← Trust Anchor (Publik)
rootca.key  ← Otoritas CA (Privat - Rahasiakan!)
```

#### 5. Algoritma Kriptografi

**🔐 Pembuatan Pasangan Kunci RSA:**
```
                    ┌─────────────────────────────┐
                    │   Pembuatan Kunci RSA       │
                    │        (2048-bit)           │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │     Keajaiban Matematika    │
                    │   p × q = n (bilangan prima)│
                    │   φ(n) = (p-1)(q-1)        │
                    │   e = 65537 (eksponen pub.) │
                    │   d ≡ e⁻¹ (mod φ(n))       │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │       Pasangan Kunci        │
                    └─────────────┬───────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                                   ▼
    ┌─────────────────────┐              ┌─────────────────────┐
    │    KUNCI PUBLIK     │              │    KUNCI PRIVAT     │
    │                     │              │                     │
    │  🔓 Untuk Verifikasi │              │  🔐 Untuk Tandatangan│
    │  • Disimpan di sert │              │  • RAHASIAKAN!      │
    │  • Boleh dibagikan  │              │  • Jangan dibagikan │
    │  • (n, e)           │              │  • (n, d)           │
    └─────────────────────┘              └─────────────────────┘
```

**🏗️ Stack Kriptografi:**
```
┌─────────────────────────────────────────────────────────────┐
│                    LAPISAN KRIPTOGRAFI                      │
├─────────────────────────────────────────────────────────────┤
│ LAPISAN APLIKASI                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ signpdf.py  │ │ Sertifikat  │ │ Tanda Tangan│            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ LIBRARY KRIPTOGRAFI (Python)                               │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │   X.509     │ │     RSA     │ │   SHA-256   │            │
│ │ Sertifikat  │ │ Enkripsi    │ │   Hashing   │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ STANDAR & FORMAT                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ Format PEM  │ │ PKCS#1 v1.5 │ │ ASN.1 DER   │            │
│ │ Base64+Teks │ │   Padding   │ │  Encoding   │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ FONDASI MATEMATIKA                                          │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ Pembuatan   │ │ Aritmatika  │ │ Fungsi Hash │            │
│ │Bilangan Prima│ │ Modular Exp │ │(Keluarga SHA)│           │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

**📊 Spesifikasi Algoritma:**
- **Pembuatan Kunci**: Kunci RSA 2048-bit
- **Hashing**: SHA-256 (Secure Hash Algorithm)
- **Padding**: Skema padding PKCS#1 v1.5
- **Format Sertifikat**: Standar X.509 v3
- **Encoding**: Format PEM (Privacy-Enhanced Mail)

#### 6. Pertimbangan Keamanan

**Keamanan Kunci Privat:**
- Kunci privat disimpan **tidak terenkripsi** untuk kemudahan (penggunaan development)
- Dalam produksi, gunakan kunci privat yang **dilindungi password**
- Simpan kunci privat di **hardware yang aman** (HSM) untuk keamanan maksimum

**Validasi Sertifikat:**
- Selalu verifikasi rantai sertifikat kembali ke Root CA terpercaya
- Periksa **tanggal kedaluwarsa** sertifikat
- Validasi **status pencabutan** sertifikat (tidak diimplementasikan dalam demo ini)

**Integritas Dokumen:**
- Setiap modifikasi pada dokumen yang ditandatangani **merusak tanda tangan**
- Perbandingan hash mendeteksi bahkan **perubahan satu bit**
- Metadata menyimpan hash asli untuk **verifikasi integritas**

### Penjelasan Struktur File

```
certificates/           # Sertifikat dan kunci privat pengguna
├── user@email.crt     # Sertifikat publik pengguna
└── user@email.key     # Kunci privat pengguna (rahasiakan!)

signatures/            # Dokumen tertandatangani dan metadata
├── dokumen_user.sig   # File tanda tangan digital
├── signed_dokumen_user.pdf  # PDF tertandatangani dengan watermark
└── metadata_dokumen_user.json  # Metadata tanda tangan

rootca.crt            # Sertifikat publik Root CA
rootca.key            # Kunci privat Root CA (rahasiakan!)
```

### Model Kepercayaan

Sistem ini menggunakan **model kepercayaan hierarkis**:
1. **Root CA** adalah trust anchor utama
2. **Sertifikat pengguna** memperoleh kepercayaan dari tanda tangan Root CA
3. **Tanda tangan dokumen** memperoleh kepercayaan dari sertifikat pengguna
4. **Verifikasi** mengikuti rantai: Dokumen → Sert. Pengguna → Root CA

## Persyaratan

- Python 3.7+
- Virtual environment (disarankan)

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/adeis/digital-signature.git
cd digital-signature
```

### 2. Buat Virtual Environment

```bash
python -m venv venv

# Di macOS/Linux:
source venv/bin/activate

# Di Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi

```bash
python signpdf.py
```

## Dependencies

Aplikasi ini menggunakan library Python berikut:

- **cryptography** - Untuk operasi kriptografi dan sertifikat X.509
- **reportlab** - Untuk pembuatan dan manipulasi PDF
- **PyPDF2** - Untuk membaca dan menulis file PDF

Lihat `requirements.txt` untuk versi lengkap dan dependencies lainnya.

## Penggunaan

Jalankan aplikasi dan ikuti prompt menu:

```bash
python signpdf.py
```

### Opsi Menu

1. **Buat Root CA** - Buat Certificate Authority (hanya sekali)
2. **Buat Sertifikat Pengguna** - Buat sertifikat untuk pengguna berdasarkan email
3. **Tandatangani Dokumen** - Tandatangani PDF atau file teks
4. **Verifikasi Tanda Tangan Dokumen (asli)** - Verifikasi menggunakan dokumen asli
5. **Verifikasi Dokumen Tertandatangani** - Verifikasi dokumen PDF yang sudah ditandatangani
6. **Daftar Sertifikat** - Tampilkan semua sertifikat pengguna
7. **Daftar Tanda Tangan** - Tampilkan semua file tanda tangan
8. **Daftar Dokumen Tertandatangani** - Tampilkan semua dokumen tertandatangani
9. **Buat Dokumen Contoh** - Buat file contoh untuk testing

### Command Line Options

Paksa buat ulang Root CA:
```bash
python signpdf.py --force
```

## Alur Kerja

### Penggunaan Pertama Kali

1. **Buat Root CA** (opsi 1) - Ini akan membuat `rootca.crt` dan `rootca.key`
2. **Buat Sertifikat Pengguna** (opsi 2) - Masukkan alamat email
3. **Buat Dokumen Contoh** (opsi 9) - Atau gunakan dokumen Anda sendiri
4. **Tandatangani Dokumen** (opsi 3) - Pilih email dan path dokumen
5. **Verifikasi Tanda Tangan** (opsi 4 atau 5) - Pastikan tanda tangan valid

### Penggunaan Sehari-hari

Setelah setup awal:
- Gunakan opsi 3 untuk menandatangani dokumen baru
- Gunakan opsi 5 untuk memverifikasi dokumen tertandatangani
- Gunakan opsi 6-8 untuk melihat daftar sertifikat dan tanda tangan

## Struktur File

Setelah menjalankan aplikasi, struktur file akan terlihat seperti ini:

```
project/
├── signpdf.py          # Aplikasi utama
├── requirements.txt       # Dependencies Python
├── certificates/          # Sertifikat dan kunci pengguna
│   ├── user@example.com.crt
│   └── user@example.com.key
├── signatures/            # Dokumen tertandatangani dan metadata
│   ├── document_user.sig
│   ├── signed_document_user.pdf
│   └── metadata_document_user.json
├── rootca.crt            # Sertifikat Root CA
├── rootca.key            # Kunci privat Root CA
└── sample.txt            # Dokumen contoh (opsional)
```

## Pertimbangan Keamanan

⚠️ **PERINGATAN PENTING**: Aplikasi ini dirancang untuk tujuan edukasi dan development. Untuk penggunaan produksi:

1. **Lindungi Kunci Privat** - Gunakan password dan simpan di tempat yang aman
2. **Gunakan HSM** - Untuk penyimpanan kunci yang lebih aman
3. **Implementasi CRL** - Tambahkan Certificate Revocation List
4. **Audit Trail** - Tambahkan logging untuk semua operasi
5. **Backup** - Backup kunci dan sertifikat secara teratur

## Contoh Penggunaan

```bash
# 1. Mulai aplikasi
python signpdf.py

# 2. Buat Root CA (pertama kali saja)
Pilih opsi: 1

# 3. Buat sertifikat pengguna
Pilih opsi: 2
Masukkan alamat email: alice@example.com

# 4. Buat dokumen contoh
Pilih opsi: 9
Masukkan path dokumen: kontrak.txt

# 5. Tandatangani dokumen
Pilih opsi: 3
Masukkan alamat email: alice@example.com
Masukkan path dokumen: kontrak.txt

# 6. Verifikasi dokumen tertandatangani
Pilih opsi: 5
Masukkan path dokumen tertandatangani: signatures/signed_kontrak_alice.pdf
```

## Troubleshooting

### Masalah Umum

**Error: Root CA not found**
- Solusi: Jalankan opsi 1 untuk membuat Root CA terlebih dahulu

**Error: Certificate for email not found**
- Solusi: Jalankan opsi 2 untuk membuat sertifikat pengguna

**Error: Document not found**
- Solusi: Pastikan path dokumen benar atau buat dokumen contoh dengan opsi 9

**Error: Signature verification failed**
- Solusi: Pastikan dokumen tidak dimodifikasi setelah ditandatangani

### Tips Debug

1. Gunakan opsi 6-8 untuk melihat daftar sertifikat dan tanda tangan yang tersedia
2. Periksa folder `certificates/` dan `signatures/` untuk memastikan file ada
3. Pastikan Root CA sudah dibuat sebelum membuat sertifikat pengguna
4. Untuk verifikasi, gunakan opsi 5 untuk dokumen PDF tertandatangani

## Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository ini
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

## Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## Penulis

Dibuat oleh Ade Iskandar
- GitHub: [@adeis](https://github.com/adeis)

## Changelog

### v1.0.0 (2025-12-18)
- Rilis awal
- Implementasi Root CA dan manajemen sertifikat pengguna
- Penandatanganan dan verifikasi dokumen
- Watermarking PDF dan manajemen metadata
- Interface CLI interaktif
- Dokumentasi lengkap dengan diagram visual
