# Multi-Signature Digital Signature System

[🇮🇩 Bahasa Indonesia](#bahasa-indonesia) | [🇺🇸 English](#english)

---

## English

### 📋 Overview

The Multi-Signature Digital Signature System allows multiple parties to digitally sign a single document in a controlled and secure manner. This system supports three different signing modes to accommodate various business workflows.

### 🎯 Key Features

- **Multiple Signing Modes**: Sequential, Independent, and Hybrid
- **Session Management**: Organized signing sessions with unique IDs
- **Role-Based Signing**: Assign roles to signers (Manager, CEO, Legal, etc.)
- **Document Integrity**: SHA-256 hash verification throughout the process
- **Audit Trail**: Complete logging of all signing activities
- **PDF Watermarking**: Final documents with multi-signature information
- **Interactive CLI**: User-friendly command-line interface

### 🔧 Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Multi-Signature Manager**:
   ```bash
   python signmulti.py
   ```

### 🚀 Quick Start Guide

#### Step 1: Create Root CA
```
Select option: 1
Force recreate if exists? (y/N): N
```

#### Step 2: Create User Certificates
```
Select option: 2
Enter email address: alice@company.com
```
Repeat for all required signers.

#### Step 3: Create Multi-Signature Session
```
Select option: 3
Enter document path: /path/to/contract.pdf
Enter required signers: alice@company.com,bob@company.com,charlie@company.com
Select signing mode (1-3): 1
Enter session name: Contract_ABC
Add roles for signers? (y/N): y
Role for alice@company.com: Manager
Role for bob@company.com: Department Head
Role for charlie@company.com: Legal Counsel
```

#### Step 4: Sign Document
```
Select option: 4
Enter session ID: Contract_ABC
Enter signer email: alice@company.com
```

#### Step 5: Verify Signatures
```
Select option: 5
Enter session ID: Contract_ABC
```

### 📊 Signing Modes

#### 1. Sequential Signing (Berurutan)
- **Use Case**: Hierarchical approval workflows
- **Behavior**: Signers must sign in a specific order
- **Example**: Manager → Department Head → Legal Counsel
- **Validation**: System enforces signing order

#### 2. Independent Signing (Paralel)
- **Use Case**: Peer-level approvals
- **Behavior**: Signers can sign in any order
- **Example**: Multiple department heads signing simultaneously
- **Validation**: No order restrictions

#### 3. Hybrid Approach (Kombinasi)
- **Use Case**: Complex workflows with mixed requirements
- **Behavior**: Combination of sequential and parallel signing
- **Example**: CEO signs first, then department heads in parallel, then legal counsel last
- **Validation**: Configurable per session

### 🗂️ File Structure

```
multisignatures/
├── SessionName_UniqueID/
│   ├── original_document.pdf          # Original document
│   ├── session_metadata.json          # Session information
│   ├── signatures/
│   │   ├── alice@company.com.sig      # Individual signatures
│   │   ├── bob@company.com.sig
│   │   └── charlie@company.com.sig
│   └── final_multisigned_document.pdf # Final signed document
```

### 📋 Session Metadata Structure

```json
{
  "session_id": "Contract_ABC_a1b2c3d4",
  "session_name": "Contract_ABC",
  "document_name": "contract.pdf",
  "document_hash_sha256": "abc123...",
  "signing_mode": "sequential",
  "status": "in_progress",
  "required_signers": ["alice@company.com", "bob@company.com"],
  "signatures": [
    {
      "signer": "alice@company.com",
      "role": "Manager",
      "signed_on": "2025-12-19 10:30:15",
      "signature_file": "signatures/alice@company.com.sig"
    }
  ],
  "current_signer_index": 1,
  "created_on": "2025-12-19 10:00:00",
  "completed_on": null
}
```

### 🔐 Security Features

- **Document Tampering Detection**: Hash comparison before each signature
- **Certificate Validation**: Verify each signer's certificate
- **Signature Independence**: Each signature is cryptographically independent
- **Role Enforcement**: Validate signer roles and permissions
- **Audit Trail**: Complete logging of all activities

### 📱 CLI Menu Options

```
1. Create Root CA                    # Initialize PKI infrastructure
2. Create User Certificate           # Generate certificates for signers
3. Create Multi-Signature Session    # Start new signing session
4. Sign Document in Session          # Add signature to session
5. Verify Multi-Signature Session    # Verify all signatures
6. List Multi-Signature Sessions     # View all sessions
7. List Certificates                 # View available certificates
8. Create Sample Document            # Generate test document
0. Exit                             # Exit application
```

### 🎯 Use Cases

#### Corporate Contracts
- **Sequential**: CEO → CFO → Legal → Department Head
- **Roles**: Executive approval hierarchy

#### Multi-Department Agreements
- **Independent**: All department heads sign in parallel
- **Roles**: Peer-level approvals

#### Complex Workflows
- **Hybrid**: CEO first, departments parallel, legal last
- **Roles**: Mixed hierarchy and peer approvals

### 🔍 Verification Process

The system performs comprehensive verification:

1. **Document Integrity**: SHA-256 hash comparison
2. **Certificate Validity**: X.509 certificate verification
3. **Signature Authenticity**: RSA signature verification
4. **Completeness Check**: All required signers present
5. **Order Validation**: Sequential mode compliance (if applicable)

### 🚨 Error Handling

Common errors and solutions:

- **Session not found**: Use correct session ID or name
- **Signer not authorized**: Ensure signer is in required signers list
- **Certificate missing**: Create user certificate first
- **Document modified**: Original document has been tampered with
- **Wrong signing order**: Sequential mode requires specific order

### 📈 Best Practices

1. **Always create Root CA first**
2. **Generate certificates for all signers before starting**
3. **Use descriptive session names**
4. **Assign meaningful roles to signers**
5. **Verify signatures after completion**
6. **Keep original documents secure**
7. **Backup session directories**

---

## Bahasa Indonesia

### 📋 Gambaran Umum

Sistem Multi-Signature Digital Signature memungkinkan beberapa pihak untuk menandatangani dokumen secara digital dengan cara yang terkontrol dan aman. Sistem ini mendukung tiga mode penandatanganan berbeda untuk mengakomodasi berbagai alur kerja bisnis.

### 🎯 Fitur Utama

- **Multiple Signing Modes**: Sequential, Independent, dan Hybrid
- **Session Management**: Sesi penandatanganan terorganisir dengan ID unik
- **Role-Based Signing**: Tetapkan peran untuk penandatangan (Manager, CEO, Legal, dll.)
- **Document Integrity**: Verifikasi hash SHA-256 sepanjang proses
- **Audit Trail**: Logging lengkap semua aktivitas penandatanganan
- **PDF Watermarking**: Dokumen akhir dengan informasi multi-signature
- **Interactive CLI**: Interface command-line yang user-friendly

### 🔧 Instalasi & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Jalankan Multi-Signature Manager**:
   ```bash
   python signmulti.py
   ```

### 🚀 Panduan Cepat

#### Langkah 1: Buat Root CA
```
Pilih opsi: 1
Force recreate if exists? (y/N): N
```

#### Langkah 2: Buat Sertifikat Pengguna
```
Pilih opsi: 2
Enter email address: alice@company.com
```
Ulangi untuk semua penandatangan yang diperlukan.

#### Langkah 3: Buat Sesi Multi-Signature
```
Pilih opsi: 3
Enter document path: /path/to/contract.pdf
Enter required signers: alice@company.com,bob@company.com,charlie@company.com
Select signing mode (1-3): 1
Enter session name: Contract_ABC
Add roles for signers? (y/N): y
Role for alice@company.com: Manager
Role for bob@company.com: Department Head
Role for charlie@company.com: Legal Counsel
```

#### Langkah 4: Tandatangani Dokumen
```
Pilih opsi: 4
Enter session ID: Contract_ABC
Enter signer email: alice@company.com
```

#### Langkah 5: Verifikasi Tanda Tangan
```
Pilih opsi: 5
Enter session ID: Contract_ABC
```

### 📊 Mode Penandatanganan

#### 1. Sequential Signing (Berurutan)
- **Use Case**: Alur kerja persetujuan hierarkis
- **Perilaku**: Penandatangan harus menandatangani dalam urutan tertentu
- **Contoh**: Manager → Department Head → Legal Counsel
- **Validasi**: Sistem memaksa urutan penandatanganan

#### 2. Independent Signing (Paralel)
- **Use Case**: Persetujuan tingkat setara
- **Perilaku**: Penandatangan dapat menandatangani dalam urutan apa pun
- **Contoh**: Beberapa kepala departemen menandatangani secara bersamaan
- **Validasi**: Tidak ada batasan urutan

#### 3. Hybrid Approach (Kombinasi)
- **Use Case**: Alur kerja kompleks dengan persyaratan campuran
- **Perilaku**: Kombinasi penandatanganan berurutan dan paralel
- **Contoh**: CEO menandatangani pertama, kemudian kepala departemen secara paralel, kemudian legal counsel terakhir
- **Validasi**: Dapat dikonfigurasi per sesi

### 🗂️ Struktur File

```
multisignatures/
├── SessionName_UniqueID/
│   ├── original_document.pdf          # Dokumen asli
│   ├── session_metadata.json          # Informasi sesi
│   ├── signatures/
│   │   ├── alice@company.com.sig      # Tanda tangan individual
│   │   ├── bob@company.com.sig
│   │   └── charlie@company.com.sig
│   └── final_multisigned_document.pdf # Dokumen akhir yang ditandatangani
```

### 📋 Struktur Metadata Sesi

```json
{
  "session_id": "Contract_ABC_a1b2c3d4",
  "session_name": "Contract_ABC",
  "document_name": "contract.pdf",
  "document_hash_sha256": "abc123...",
  "signing_mode": "sequential",
  "status": "in_progress",
  "required_signers": ["alice@company.com", "bob@company.com"],
  "signatures": [
    {
      "signer": "alice@company.com",
      "role": "Manager",
      "signed_on": "2025-12-19 10:30:15",
      "signature_file": "signatures/alice@company.com.sig"
    }
  ],
  "current_signer_index": 1,
  "created_on": "2025-12-19 10:00:00",
  "completed_on": null
}
```

### 🔐 Fitur Keamanan

- **Deteksi Manipulasi Dokumen**: Perbandingan hash sebelum setiap tanda tangan
- **Validasi Sertifikat**: Verifikasi sertifikat setiap penandatangan
- **Independensi Tanda Tangan**: Setiap tanda tangan secara kriptografis independen
- **Penegakan Peran**: Validasi peran dan izin penandatangan
- **Audit Trail**: Logging lengkap semua aktivitas

### 📱 Opsi Menu CLI

```
1. Create Root CA                    # Inisialisasi infrastruktur PKI
2. Create User Certificate           # Generate sertifikat untuk penandatangan
3. Create Multi-Signature Session    # Mulai sesi penandatanganan baru
4. Sign Document in Session          # Tambahkan tanda tangan ke sesi
5. Verify Multi-Signature Session    # Verifikasi semua tanda tangan
6. List Multi-Signature Sessions     # Lihat semua sesi
7. List Certificates                 # Lihat sertifikat yang tersedia
8. Create Sample Document            # Generate dokumen test
0. Exit                             # Keluar aplikasi
```

### 🎯 Kasus Penggunaan

#### Kontrak Korporat
- **Sequential**: CEO → CFO → Legal → Department Head
- **Peran**: Hierarki persetujuan eksekutif

#### Perjanjian Multi-Departemen
- **Independent**: Semua kepala departemen menandatangani secara paralel
- **Peran**: Persetujuan tingkat setara

#### Alur Kerja Kompleks
- **Hybrid**: CEO pertama, departemen paralel, legal terakhir
- **Peran**: Campuran hierarki dan persetujuan setara

### 🔍 Proses Verifikasi

Sistem melakukan verifikasi komprehensif:

1. **Integritas Dokumen**: Perbandingan hash SHA-256
2. **Validitas Sertifikat**: Verifikasi sertifikat X.509
3. **Keaslian Tanda Tangan**: Verifikasi tanda tangan RSA
4. **Pemeriksaan Kelengkapan**: Semua penandatangan yang diperlukan hadir
5. **Validasi Urutan**: Kepatuhan mode berurutan (jika berlaku)

### 🚨 Penanganan Error

Error umum dan solusi:

- **Session not found**: Gunakan session ID atau nama yang benar
- **Signer not authorized**: Pastikan penandatangan ada dalam daftar yang diperlukan
- **Certificate missing**: Buat sertifikat pengguna terlebih dahulu
- **Document modified**: Dokumen asli telah dimanipulasi
- **Wrong signing order**: Mode berurutan memerlukan urutan tertentu

### 📈 Best Practices

1. **Selalu buat Root CA terlebih dahulu**
2. **Generate sertifikat untuk semua penandatangan sebelum memulai**
3. **Gunakan nama sesi yang deskriptif**
4. **Tetapkan peran yang bermakna untuk penandatangan**
5. **Verifikasi tanda tangan setelah selesai**
6. **Jaga keamanan dokumen asli**
7. **Backup direktori sesi**

---

## 📞 Support

Untuk pertanyaan atau masalah, silakan buka issue di repository ini atau hubungi tim pengembang.

## 📄 License

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.
