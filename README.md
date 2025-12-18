# Digital Signature Manager

A comprehensive Python application for creating and managing digital signatures using X.509 certificates. This tool allows you to create a Certificate Authority (CA), generate user certificates, sign documents, and verify digital signatures.

## Features

- 🔐 **Root CA Management** - Create and manage your own Certificate Authority
- 👤 **User Certificate Generation** - Create certificates for users based on email addresses
- ✍️ **Document Signing** - Sign PDF and text documents with digital signatures
- ✅ **Signature Verification** - Verify the authenticity of signed documents
- 🔍 **Document Integrity Check** - Ensure documents haven't been tampered with
- 📄 **PDF Watermarking** - Add signature watermarks to signed PDF documents
- 📊 **Metadata Management** - Store and retrieve signature metadata in JSON format

## Concept

### What is Digital Signature?

Digital signatures are cryptographic mechanisms that provide:
- **Authentication** - Verify the identity of the signer
- **Integrity** - Ensure the document hasn't been modified
- **Non-repudiation** - Prevent the signer from denying they signed the document

### Key Components

#### 1. Root Certificate Authority (Root CA)
The **Root CA** is the foundation of trust in our digital signature system:
- Acts as the **trusted third party** that issues and validates certificates
- Has a **self-signed certificate** (it signs its own certificate)
- Contains a **public-private key pair**:
  - **Private key**: Used to sign user certificates (kept secret)
  - **Public key**: Used to verify certificates issued by this CA
- **Validity period**: Typically 10 years (3650 days)
- **Trust anchor**: All certificates in the system derive their trust from the Root CA

#### 2. User Certificates (X.509)
User certificates are **digital identity cards** that contain:
- **Public key** of the user
- **Identity information** (email, name, organization)
- **Digital signature from Root CA** (proves authenticity)
- **Validity period** (typically 1 year)
- **Serial number** (unique identifier)

**Certificate Chain of Trust:**
```
Root CA (self-signed) → User Certificate (signed by Root CA)
```

#### 3. Digital Signature Process

**📝 Signing Process Flow:**
```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Document   │───▶│  SHA-256    │───▶│ Document Hash│
│ (original)   │    │  Hashing    │    │   (256-bit)  │
└──────────────┘    └─────────────┘    └──────┬───────┘
                                              │
                    ┌─────────────┐          │
                    │ User Private│          │
                    │    Key      │          │
                    │ (RSA 2048)  │          │
                    └──────┬──────┘          │
                           │                 │
                           ▼                 ▼
                    ┌─────────────────────────────┐
                    │     RSA Encryption          │
                    │   (PKCS#1 v1.5 Padding)    │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │    Digital Signature        │
                    │      (.sig file)            │
                    └─────────────────────────────┘
```

**✅ Verification Process Flow:**
```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Document   │───▶│  SHA-256    │───▶│ Current Hash │
│ (to verify)  │    │  Hashing    │    │   (256-bit)  │
└──────────────┘    └─────────────┘    └──────┬───────┘
                                              │
┌──────────────┐    ┌─────────────┐          │
│   Digital    │───▶│ User Public │          │
│  Signature   │    │    Key      │          │
│ (.sig file)  │    │ (from cert) │          │
└──────────────┘    └──────┬──────┘          │
                           │                 │
                           ▼                 ▼
                    ┌─────────────────────────────┐
                    │     RSA Decryption          │
                    │   → Original Hash           │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │    Hash Comparison          │
                    │ Original == Current ?       │
                    │                             │
                    │ ✅ MATCH = AUTHENTIC        │
                    │ ❌ NO MATCH = TAMPERED      │
                    └─────────────────────────────┘
```

#### 4. Public Key Infrastructure (PKI)

**🏗️ PKI Architecture:**
```
                    ┌─────────────────────────────────┐
                    │         ROOT CA                 │
                    │    ┌─────────────────────┐      │
                    │    │   Private Key       │      │ ← Self-signed
                    │    │   (rootca.key)      │      │   Trust Anchor
                    │    └─────────────────────┘      │
                    │    ┌─────────────────────┐      │
                    │    │  Public Certificate │      │
                    │    │   (rootca.crt)      │      │
                    │    └─────────────────────┘      │
                    └─────────────┬───────────────────┘
                                  │ signs & issues
                                  ▼
        ┌─────────────────────────────────────────────────────────┐
        │                USER CERTIFICATES                        │
        │  ┌─────────────────┐    ┌─────────────────┐            │
        │  │ alice@email.crt │    │  bob@email.crt  │    ...     │
        │  │ alice@email.key │    │  bob@email.key  │            │
        │  └─────────────────┘    └─────────────────┘            │
        └─────────────┬───────────────────┬─────────────────────┘
                      │                   │
                      ▼                   ▼
        ┌─────────────────────┐  ┌─────────────────────┐
        │   ALICE SIGNS       │  │    BOB SIGNS        │
        │                     │  │                     │
        │ ┌─────────────────┐ │  │ ┌─────────────────┐ │
        │ │ contract.pdf    │ │  │ │ report.txt      │ │
        │ │ + signature     │ │  │ │ + signature     │ │
        │ └─────────────────┘ │  │ └─────────────────┘ │
        └─────────────────────┘  └─────────────────────┘
```

**🔄 Complete Workflow Diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    DIGITAL SIGNATURE WORKFLOW                   │
└─────────────────────────────────────────────────────────────────┘

1️⃣ SETUP PHASE
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Create    │───▶│   Create    │───▶│   Ready to  │
│  Root CA    │    │ User Certs  │    │    Sign     │
└─────────────┘    └─────────────┘    └─────────────┘

2️⃣ SIGNING PHASE
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Original   │───▶│   Hash      │───▶│   Encrypt   │───▶│  Signature  │
│  Document   │    │ (SHA-256)   │    │ with Priv   │    │   Created   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

3️⃣ VERIFICATION PHASE
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Document   │───▶│   Hash      │───▶│   Compare   │───▶│   Result    │
│ + Signature │    │ + Decrypt   │    │   Hashes    │    │ ✅ or ❌    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

4️⃣ FILE STRUCTURE
certificates/
├── alice@email.crt  ┐
├── alice@email.key  ├─ User Identity
├── bob@email.crt    │
└── bob@email.key    ┘

signatures/
├── contract_alice.sig        ┐
├── signed_contract_alice.pdf ├─ Signed Documents
├── metadata_contract_alice.json ┘
├── report_bob.sig           ┐
├── signed_report_bob.pdf    ├─ Signed Documents  
└── metadata_report_bob.json ┘

rootca.crt  ← Trust Anchor (Public)
rootca.key  ← CA Authority (Private - Keep Secret!)
```

#### 5. Cryptographic Algorithms

**🔐 RSA Key Pair Generation:**
```
                    ┌─────────────────────────────┐
                    │     RSA Key Generation      │
                    │        (2048-bit)           │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │     Mathematical Magic      │
                    │   p × q = n (large primes)  │
                    │   φ(n) = (p-1)(q-1)        │
                    │   e = 65537 (public exp)    │
                    │   d ≡ e⁻¹ (mod φ(n))       │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │         Key Pair            │
                    └─────────────┬───────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                                   ▼
    ┌─────────────────────┐              ┌─────────────────────┐
    │    PUBLIC KEY       │              │    PRIVATE KEY      │
    │                     │              │                     │
    │  🔓 For Verification │              │  🔐 For Signing     │
    │  • Stored in cert   │              │  • Keep SECRET!     │
    │  • Can be shared    │              │  • Never share      │
    │  • (n, e)           │              │  • (n, d)           │
    └─────────────────────┘              └─────────────────────┘
```

**🏗️ Cryptographic Stack:**
```
┌─────────────────────────────────────────────────────────────┐
│                    CRYPTOGRAPHIC LAYERS                     │
├─────────────────────────────────────────────────────────────┤
│ APPLICATION LAYER                                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ signpdf.py  │ │ Certificates│ │ Signatures  │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ CRYPTOGRAPHY LIBRARY (Python)                              │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │   X.509     │ │     RSA     │ │   SHA-256   │            │
│ │ Certificates│ │ Encryption  │ │   Hashing   │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ STANDARDS & FORMATS                                         │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ PEM Format  │ │ PKCS#1 v1.5 │ │ ASN.1 DER   │            │
│ │ Base64+Text │ │   Padding   │ │  Encoding   │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
├─────────────────────────────────────────────────────────────┤
│ MATHEMATICAL FOUNDATION                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │ Prime Number│ │ Modular Exp │ │ Hash Function│           │
│ │ Generation  │ │ Arithmetic  │ │ (SHA Family) │           │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

**📊 Algorithm Specifications:**
- **Key Generation**: RSA 2048-bit keys
- **Hashing**: SHA-256 (Secure Hash Algorithm)
- **Padding**: PKCS#1 v1.5 padding scheme
- **Certificate Format**: X.509 v3 standard
- **Encoding**: PEM (Privacy-Enhanced Mail) format

#### 6. Security Considerations

**Private Key Security:**
- Private keys are stored **unencrypted** for simplicity (development use)
- In production, use **password-protected** private keys
- Store private keys in **secure hardware** (HSM) for maximum security

**Certificate Validation:**
- Always verify certificate chain back to trusted Root CA
- Check certificate **expiration dates**
- Validate certificate **revocation status** (not implemented in this demo)

**Document Integrity:**
- Any modification to signed document **breaks the signature**
- Hash comparison detects even **single bit changes**
- Metadata stores original hash for **integrity verification**

### File Structure Explained

```
certificates/           # User certificates and private keys
├── user@email.crt     # User's public certificate
└── user@email.key     # User's private key (keep secret!)

signatures/            # Signed documents and metadata
├── document_user.sig  # Digital signature file
├── signed_document_user.pdf  # Signed PDF with watermark
└── metadata_document_user.json  # Signature metadata

rootca.crt            # Root CA public certificate
rootca.key            # Root CA private key (keep secret!)
```

### Trust Model

This system uses a **hierarchical trust model**:
1. **Root CA** is the ultimate trust anchor
2. **User certificates** derive trust from Root CA signature
3. **Document signatures** derive trust from user certificates
4. **Verification** follows the chain: Document → User Cert → Root CA

## Requirements

- Python 3.7+
- Virtual environment (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/digital-signature-manager.git
cd digital-signature-manager
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python signpdf.py
```

## Dependencies

The application requires the following Python packages:

- `cryptography` - For cryptographic operations and X.509 certificate handling
- `reportlab` - For PDF generation and manipulation
- `PyPDF2` - For PDF reading and watermarking

## Usage

### Interactive Mode

Run the application and follow the menu prompts:

```bash
python signpdf.py
```

### Menu Options

```
==================================================
    DIGITAL SIGNATURE MANAGER
==================================================
1. Create Root CA
2. Create User Certificate
3. Sign Document
4. Verify Document Signature (original)
5. Verify Signed Document
6. List Certificates
7. List Signatures
8. List Signed Documents
9. Create Sample Document
0. Exit
```

### Command Line Mode

Force recreate Root CA:
```bash
python signpdf.py --force
```

## Workflow

### 1. Initial Setup

1. **Create Root CA** (Option 1)
   - Creates `rootca.crt` and `rootca.key`
   - Only needs to be done once
   - Use `--force` flag to recreate if needed

### 2. User Management

2. **Create User Certificate** (Option 2)
   - Enter user's email address
   - Generates certificate and private key in `certificates/` folder
   - Format: `email.crt` and `email.key`

### 3. Document Signing

3. **Sign Document** (Option 3)
   - Select user email from available certificates
   - Provide path to document (PDF or text)
   - Generates:
     - Signature file (`.sig`)
     - Metadata file (`.json`)
     - Signed PDF with watermark

### 4. Verification

**Option 4: Verify Original Document**
- For verifying original documents against signature files
- Requires: original document + email + signature file

**Option 5: Verify Signed Document** ⭐ **Recommended**
- For verifying documents that have already been signed
- Automatically reads metadata and verifies authenticity
- Only requires: path to signed document

## File Structure

```
project/
├── signpdf.py          # Main application
├── requirements.txt       # Python dependencies
├── certificates/          # User certificates and keys
│   ├── user@example.com.crt
│   └── user@example.com.key
├── signatures/           # Signed documents and metadata
│   ├── signed_document_user@example.com.pdf
│   ├── document_user@example.com.sig
│   └── metadata_document_user@example.com.json
├── rootca.crt           # Root Certificate Authority certificate
└── rootca.key           # Root Certificate Authority private key
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Private Keys**: Keep all `.key` files secure and never share them
2. **Root CA**: The `rootca.key` file is especially sensitive - protect it carefully
3. **Certificates**: Store certificates in a secure location
4. **Backup**: Regularly backup your certificates and keys
5. **Production Use**: For production environments, consider using hardware security modules (HSM)

## Examples

### Example 1: Complete Workflow

```bash
# 1. Start the application
python signpdf.py

# 2. Create Root CA (first time only)
Select option: 1

# 3. Create user certificate
Select option: 2
Enter email: john.doe@company.com

# 4. Sign a document
Select option: 3
Enter email: john.doe@company.com
Enter document path: /path/to/document.pdf

# 5. Verify signed document
Select option: 5
Enter signed document path: signatures/signed_document_john.doe@company.com.pdf
```

### Example 2: Verification Output

```
📄 SIGNED DOCUMENT VERIFICATION
==================================================
Signed document: signatures/signed_contract_john.doe@company.com.pdf
Original document: /documents/contract.pdf
Signed by: john.doe@company.com
Signed on: 2025-12-18 10:30:15
Certificate: certificates/john.doe@company.com.crt

🔍 VERIFYING SIGNATURE...
✅ Signature is VALID and document is AUTHENTIC.

✅ DOCUMENT VERIFICATION SUCCESSFUL!
✅ The signed document is authentic and was signed by john.doe@company.com
✅ Original document integrity confirmed
✅ Document integrity check: PASSED
```

## Troubleshooting

### Common Issues

1. **"Root CA not found"**
   - Run option 1 to create Root CA first

2. **"Certificate not found"**
   - Create user certificate using option 2

3. **"Document not found"**
   - Check file path and ensure file exists

4. **"Signature verification failed"**
   - Ensure you're using the correct original document
   - Check that the document hasn't been modified after signing

### Getting Help

- Check that all dependencies are installed: `pip list`
- Verify Python version: `python --version`
- Ensure virtual environment is activated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and development purposes. For production use in critical applications, please consult with security professionals and consider using established PKI solutions.

## Author

Created by Ade Iskandar
- GitHub: [@adeis](https://github.com/adeis)


## Changelog

### v1.0.0 (2025-12-18)
- Initial release
- Root CA creation and management
- User certificate generation
- Document signing with PDF watermarking
- Signature verification
- Metadata management
- Interactive CLI interface
