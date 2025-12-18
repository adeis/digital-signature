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
