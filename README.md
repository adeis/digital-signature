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

**Signing Process:**
1. **Hash Generation**: Create SHA-256 hash of the document
2. **Encryption**: Encrypt the hash with user's **private key**
3. **Signature Creation**: The encrypted hash becomes the digital signature
4. **Attachment**: Attach signature to document with metadata

**Verification Process:**
1. **Signature Decryption**: Decrypt signature with user's **public key**
2. **Hash Comparison**: Compare decrypted hash with fresh document hash
3. **Certificate Validation**: Verify user certificate against Root CA
4. **Result**: If hashes match and certificate is valid → **AUTHENTIC**

#### 4. Public Key Infrastructure (PKI)

Our system implements a simplified PKI:

```
┌─────────────────┐
│    Root CA      │ ← Self-signed, trusted anchor
│  (rootca.crt)   │
└─────────┬───────┘
          │ signs
          ▼
┌─────────────────┐
│ User Certificate│ ← Signed by Root CA
│ (user@email.crt)│
└─────────┬───────┘
          │ used for
          ▼
┌─────────────────┐
│ Digital Signature│ ← Signs documents
│ (document.sig)  │
└─────────────────┘
```

#### 5. Cryptographic Algorithms

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
