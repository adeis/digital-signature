import os
import sys
import hashlib
import datetime
import argparse
import json
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import (
    Name, NameAttribute, NameOID, CertificateBuilder, load_pem_x509_certificate
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red, black
from reportlab.lib.units import inch
from PyPDF2 import PdfReader, PdfWriter
import io

class DigitalSignatureManager:
    def __init__(self):
        self.root_ca_cert_path = "rootca.crt"
        self.root_ca_key_path = "rootca.key"
        self.certs_dir = "certificates"
        self.signatures_dir = "signatures"
        
        # Buat direktori jika belum ada
        Path(self.certs_dir).mkdir(exist_ok=True)
        Path(self.signatures_dir).mkdir(exist_ok=True)

    def create_root_ca(self, force=False):
        """Membuat Root CA"""
        if os.path.exists(self.root_ca_cert_path) and os.path.exists(self.root_ca_key_path) and not force:
            print("Root CA already exists. Use --force to recreate.")
            return True

        if force:
            print("Force recreating Root CA...")

        # Membuat kunci privat untuk Root CA
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = Name([
            NameAttribute(NameOID.COUNTRY_NAME, u"ID"),
            NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Jakarta"),
            NameAttribute(NameOID.LOCALITY_NAME, u"Jakarta"),
            NameAttribute(NameOID.ORGANIZATION_NAME, u"Digital Signature Root CA"),
            NameAttribute(NameOID.COMMON_NAME, u"Digital Signature Root CA"),
        ])

        cert_builder = (
            CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
            .serial_number(1000)
            .public_key(key.public_key())
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True,
            )
        )
        cert = cert_builder.sign(private_key=key, algorithm=hashes.SHA256())

        # Simpan sertifikat dan private key ke file
        with open(self.root_ca_cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        with open(self.root_ca_key_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        print(f"Root CA created and saved to {self.root_ca_cert_path} and {self.root_ca_key_path}")
        return True

    def create_user_certificate(self, email):
        """Membuat sertifikat pengguna berdasarkan email"""
        if not os.path.exists(self.root_ca_cert_path) or not os.path.exists(self.root_ca_key_path):
            print("Root CA not found. Please create Root CA first.")
            return False

        # Path untuk sertifikat dan kunci pengguna
        user_cert_path = os.path.join(self.certs_dir, f"{email}.crt")
        user_key_path = os.path.join(self.certs_dir, f"{email}.key")

        if os.path.exists(user_cert_path) and os.path.exists(user_key_path):
            print(f"Certificate for {email} already exists.")
            return True

        # Membuat kunci privat untuk pengguna
        user_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Simpan kunci privat pengguna
        with open(user_key_path, "wb") as f:
            f.write(user_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        # Baca Root CA
        with open(self.root_ca_cert_path, "rb") as f:
            ca_cert = load_pem_x509_certificate(f.read())

        with open(self.root_ca_key_path, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)

        # Buat sertifikat pengguna
        user_subject = Name([
            NameAttribute(NameOID.COUNTRY_NAME, u"ID"),
            NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Jakarta"),
            NameAttribute(NameOID.LOCALITY_NAME, u"Jakarta"),
            NameAttribute(NameOID.ORGANIZATION_NAME, u"Digital Signature User"),
            NameAttribute(NameOID.COMMON_NAME, email),
            NameAttribute(NameOID.EMAIL_ADDRESS, email),
        ])

        user_cert_builder = (
            CertificateBuilder()
            .subject_name(user_subject)
            .issuer_name(ca_cert.subject)
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .serial_number(hash(email) % (2**32))  # Serial number berdasarkan hash email
            .public_key(user_key.public_key())
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
        )

        user_cert = user_cert_builder.sign(
            private_key=ca_key,
            algorithm=hashes.SHA256(),
        )

        # Simpan sertifikat pengguna
        with open(user_cert_path, "wb") as f:
            f.write(user_cert.public_bytes(serialization.Encoding.PEM))

        print(f"User certificate created for {email}")
        print(f"Certificate: {user_cert_path}")
        print(f"Private key: {user_key_path}")
        return True

    def sign_document(self, email, document_path):
        """Menandatangani dokumen berdasarkan email dan path dokumen"""
        user_key_path = os.path.join(self.certs_dir, f"{email}.key")
        user_cert_path = os.path.join(self.certs_dir, f"{email}.crt")

        if not os.path.exists(user_key_path) or not os.path.exists(user_cert_path):
            print(f"Certificate for {email} not found. Please create user certificate first.")
            return False

        if not os.path.exists(document_path):
            print(f"Document {document_path} not found.")
            return False

        # Load user private key
        with open(user_key_path, "rb") as f:
            user_private_key = serialization.load_pem_private_key(f.read(), password=None)

        # Read document
        with open(document_path, "rb") as f:
            document_data = f.read()

        # Create document hash
        document_hash = hashlib.sha256(document_data).digest()

        # Sign document hash
        signature = user_private_key.sign(
            document_hash,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Create signature file path
        doc_name = Path(document_path).stem
        signature_path = os.path.join(self.signatures_dir, f"{doc_name}_{email}.sig")

        # Save signature
        with open(signature_path, "wb") as f:
            f.write(signature)

        # Create signed PDF path
        signed_doc_path = os.path.join(self.signatures_dir, f"signed_{doc_name}_{email}.pdf")
        
        # Create signature metadata
        sign_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        metadata = {
            "original_document": document_path,
            "signed_by": email,
            "signed_on": sign_time,
            "signature_file": signature_path,
            "document_hash_sha256": document_hash.hex(),
            "signature_hex": signature.hex(),
            "certificate_path": user_cert_path
        }
        
        # Save metadata
        metadata_path = os.path.join(self.signatures_dir, f"metadata_{doc_name}_{email}.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        try:
            if document_path.lower().endswith('.pdf'):
                # Handle PDF files - copy original and add watermark
                self._create_signed_pdf_with_watermark(document_path, signed_doc_path, metadata)
            else:
                # Handle non-PDF files - create new PDF with original content
                self._create_signed_pdf_from_text(document_path, signed_doc_path, metadata)
                
            print(f"Document signed successfully!")
            print(f"Signature file: {signature_path}")
            print(f"Metadata file: {metadata_path}")
            print(f"Signed document: {signed_doc_path}")
            return True
            
        except Exception as e:
            print(f"Error creating signed PDF: {e}")
            return False

    def _create_signed_pdf_with_watermark(self, original_pdf_path, signed_pdf_path, metadata):
        """Copy PDF asli dan tambahkan watermark signature"""
        # Read original PDF
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()
        
        # Create watermark with signature info
        watermark_buffer = io.BytesIO()
        c = canvas.Canvas(watermark_buffer, pagesize=letter)
        
        # Set transparency and color for watermark
        c.setFillColor(red, alpha=0.3)
        c.setFont("Helvetica-Bold", 10)
        
        # Add watermark text at bottom of page
        c.drawString(50, 50, f"DIGITALLY SIGNED by {metadata['signed_by']}")
        c.drawString(50, 35, f"Signed on: {metadata['signed_on']}")
        c.drawString(50, 20, f"Hash: {metadata['document_hash_sha256'][:32]}...")
        
        c.save()
        watermark_buffer.seek(0)
        
        # Create watermark PDF
        watermark_pdf = PdfReader(watermark_buffer)
        watermark_page = watermark_pdf.pages[0]
        
        # Add watermark to each page
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        # Add metadata to PDF
        writer.add_metadata({
            '/Title': f'Signed Document - {Path(metadata["original_document"]).name}',
            '/Author': metadata['signed_by'],
            '/Subject': 'Digitally Signed Document',
            '/Creator': 'Digital Signature Manager',
            '/Producer': 'Digital Signature Manager',
            '/CreationDate': f"D:{metadata['signed_on'].replace('-', '').replace(' ', '').replace(':', '')}",
            '/ModDate': f"D:{metadata['signed_on'].replace('-', '').replace(' ', '').replace(':', '')}"
        })
        
        # Save signed PDF
        with open(signed_pdf_path, "wb") as output_file:
            writer.write(output_file)

    def _create_signed_pdf_from_text(self, original_file_path, signed_pdf_path, metadata):
        """Create PDF from non-PDF file dengan signature info"""
        c = canvas.Canvas(signed_pdf_path, pagesize=letter)
        
        # Header dengan signature info
        c.setFillColor(red)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, "DIGITALLY SIGNED DOCUMENT")
        
        c.setFillColor(black)
        c.setFont("Helvetica", 10)
        c.drawString(100, 730, f"Original document: {metadata['original_document']}")
        c.drawString(100, 715, f"Signed by: {metadata['signed_by']}")
        c.drawString(100, 700, f"Signed on: {metadata['signed_on']}")
        c.drawString(100, 685, f"Document hash (SHA256): {metadata['document_hash_sha256'][:64]}...")
        c.drawString(100, 670, f"Signature (hex): {metadata['signature_hex'][:64]}...")
        
        # Separator line
        c.line(100, 660, 500, 660)
        
        # Original content
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 640, "ORIGINAL DOCUMENT CONTENT:")
        
        try:
            with open(original_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            c.setFont("Helvetica", 9)
            y_pos = 620
            line_height = 12
            max_chars_per_line = 80
            
            for line in content.split('\n'):
                if y_pos < 50:  # Start new page if needed
                    c.showPage()
                    y_pos = 750
                
                # Wrap long lines
                while len(line) > max_chars_per_line:
                    c.drawString(120, y_pos, line[:max_chars_per_line])
                    line = line[max_chars_per_line:]
                    y_pos -= line_height
                    if y_pos < 50:
                        c.showPage()
                        y_pos = 750
                
                c.drawString(120, y_pos, line)
                y_pos -= line_height
                
        except Exception as e:
            c.drawString(120, 620, f"Error reading original file: {e}")
        
        c.save()

    def verify_signature(self, email, document_path, signature_path=None):
        """Verifikasi tanda tangan dokumen"""
        user_cert_path = os.path.join(self.certs_dir, f"{email}.crt")

        if not os.path.exists(user_cert_path):
            print(f"Certificate for {email} not found.")
            return False

        if not os.path.exists(document_path):
            print(f"Document {document_path} not found.")
            return False

        # Auto-detect signature path if not provided
        if signature_path is None:
            doc_name = Path(document_path).stem
            signature_path = os.path.join(self.signatures_dir, f"{doc_name}_{email}.sig")

        if not os.path.exists(signature_path):
            print(f"Signature file {signature_path} not found.")
            return False

        # Load user certificate
        with open(user_cert_path, "rb") as f:
            user_cert = load_pem_x509_certificate(f.read())

        # Load signature
        with open(signature_path, "rb") as f:
            signature = f.read()

        # Load document
        with open(document_path, "rb") as f:
            document_data = f.read()

        # Create document hash
        document_hash = hashlib.sha256(document_data).digest()

        # Verify signature
        public_key = user_cert.public_key()

        try:
            public_key.verify(
                signature,
                document_hash,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print("✅ Signature is VALID and document is AUTHENTIC.")
            print(f"Document: {document_path}")
            print(f"Signed by: {email}")
            print(f"Signature file: {signature_path}")
            return True
        except Exception as e:
            print("❌ Signature verification FAILED.")
            print(f"Error: {e}")
            return False

    def verify_signed_document(self, signed_pdf_path):
        """Verifikasi dokumen PDF yang sudah ditandatangani menggunakan metadata"""
        if not os.path.exists(signed_pdf_path):
            print(f"Signed document {signed_pdf_path} not found.")
            return False

        # Extract info from filename
        signed_filename = Path(signed_pdf_path).stem
        if not signed_filename.startswith('signed_'):
            print("This doesn't appear to be a signed document (filename should start with 'signed_')")
            return False

        # Parse filename: signed_docname_email.pdf
        parts = signed_filename.replace('signed_', '').rsplit('_', 1)
        if len(parts) != 2:
            print("Cannot parse signed document filename. Expected format: signed_docname_email.pdf")
            return False

        doc_name, email = parts

        # Look for metadata file
        metadata_path = os.path.join(self.signatures_dir, f"metadata_{doc_name}_{email}.json")
        if not os.path.exists(metadata_path):
            print(f"Metadata file not found: {metadata_path}")
            print("This document may not have been signed with this system.")
            return False

        try:
            # Load metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            print(f"\n📄 SIGNED DOCUMENT VERIFICATION")
            print(f"=" * 50)
            print(f"Signed document: {signed_pdf_path}")
            print(f"Original document: {metadata['original_document']}")
            print(f"Signed by: {metadata['signed_by']}")
            print(f"Signed on: {metadata['signed_on']}")
            print(f"Certificate: {metadata['certificate_path']}")

            # Check if original document still exists
            original_doc = metadata['original_document']
            if not os.path.exists(original_doc):
                print(f"\n⚠️  WARNING: Original document not found at {original_doc}")
                print("Cannot verify signature without original document.")
                
                # Show stored hash for reference
                print(f"\n📋 STORED SIGNATURE INFO:")
                print(f"Document hash (SHA256): {metadata['document_hash_sha256']}")
                print(f"Signature (hex): {metadata['signature_hex'][:64]}...")
                return False

            # Verify signature using original document
            signature_path = metadata['signature_file']
            if not os.path.exists(signature_path):
                print(f"\n❌ Signature file not found: {signature_path}")
                return False

            # Perform actual verification
            print(f"\n🔍 VERIFYING SIGNATURE...")
            result = self.verify_signature(email, original_doc, signature_path)
            
            if result:
                print(f"\n✅ DOCUMENT VERIFICATION SUCCESSFUL!")
                print(f"✅ The signed document is authentic and was signed by {email}")
                print(f"✅ Original document integrity confirmed")
                
                # Additional checks
                self._verify_document_integrity(original_doc, metadata)
                
            return result

        except json.JSONDecodeError:
            print(f"❌ Invalid metadata file: {metadata_path}")
            return False
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False

    def _verify_document_integrity(self, original_doc, metadata):
        """Verify that original document hasn't been tampered with"""
        try:
            with open(original_doc, "rb") as f:
                current_data = f.read()
            
            current_hash = hashlib.sha256(current_data).hexdigest()
            stored_hash = metadata['document_hash_sha256']
            
            if current_hash == stored_hash:
                print(f"✅ Document integrity check: PASSED")
            else:
                print(f"⚠️  Document integrity check: FAILED")
                print(f"   Current hash:  {current_hash}")
                print(f"   Original hash: {stored_hash}")
                print(f"   The original document may have been modified after signing!")
                
        except Exception as e:
            print(f"⚠️  Could not verify document integrity: {e}")

    def list_signed_documents(self):
        """List semua dokumen yang sudah ditandatangani"""
        print("\n=== Available Signed Documents ===")
        signed_files = list(Path(self.signatures_dir).glob("signed_*.pdf"))
        
        if not signed_files:
            print("No signed documents found.")
            return
            
        for signed_file in signed_files:
            # Parse filename to get info
            filename = signed_file.stem
            parts = filename.replace('signed_', '').rsplit('_', 1)
            if len(parts) == 2:
                doc_name, email = parts
                metadata_path = os.path.join(self.signatures_dir, f"metadata_{doc_name}_{email}.json")
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                        print(f"  📄 {signed_file.name}")
                        print(f"     Signed by: {email}")
                        print(f"     Signed on: {metadata.get('signed_on', 'Unknown')}")
                        print(f"     Original: {Path(metadata.get('original_document', 'Unknown')).name}")
                        print()
                    except:
                        print(f"  📄 {signed_file.name} (metadata error)")
                else:
                    print(f"  📄 {signed_file.name} (no metadata)")
            else:
                print(f"  📄 {signed_file.name} (unknown format)")

    def list_certificates(self):
        """List semua sertifikat yang ada"""
        print("\n=== Available Certificates ===")
        cert_files = list(Path(self.certs_dir).glob("*.crt"))
        
        if not cert_files:
            print("No user certificates found.")
            return
            
        for cert_file in cert_files:
            email = cert_file.stem
            key_file = cert_file.with_suffix('.key')
            status = "✅" if key_file.exists() else "❌ (missing key)"
            print(f"  {email} {status}")

    def list_signatures(self):
        """List semua signature yang ada"""
        print("\n=== Available Signatures ===")
        sig_files = list(Path(self.signatures_dir).glob("*.sig"))
        
        if not sig_files:
            print("No signatures found.")
            return
            
        for sig_file in sig_files:
            print(f"  {sig_file.name}")

def create_sample_document(path):
    """Membuat dokumen contoh untuk testing"""
    with open(path, "w") as f:
        f.write("This is a sample document for digital signature testing.\n")
        f.write(f"Created on: {datetime.datetime.now()}\n")
        f.write("This document contains important information that needs to be signed.\n")
    print(f"Sample document created: {path}")

def main():
    dsm = DigitalSignatureManager()
    
    if len(sys.argv) > 1:
        # Command line mode
        parser = argparse.ArgumentParser(description='Digital Signature Manager')
        parser.add_argument('--force', action='store_true', help='Force recreate Root CA')
        args = parser.parse_args()
        
        if args.force:
            dsm.create_root_ca(force=True)
            return
    
    # Interactive mode
    while True:
        print("\n" + "="*50)
        print("    DIGITAL SIGNATURE MANAGER")
        print("="*50)
        print("1. Create Root CA")
        print("2. Create User Certificate")
        print("3. Sign Document")
        print("4. Verify Document Signature (original)")
        print("5. Verify Signed Document")
        print("6. List Certificates")
        print("7. List Signatures")
        print("8. List Signed Documents")
        print("9. Create Sample Document")
        print("0. Exit")
        print("-"*50)
        
        try:
            choice = input("Select option (0-9): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
                
            elif choice == "1":
                force = input("Force recreate if exists? (y/N): ").strip().lower() == 'y'
                dsm.create_root_ca(force=force)
                
            elif choice == "2":
                email = input("Enter email address: ").strip()
                if email:
                    dsm.create_user_certificate(email)
                else:
                    print("Email address is required.")
                    
            elif choice == "3":
                dsm.list_certificates()
                email = input("\nEnter email address: ").strip()
                document_path = input("Enter document path: ").strip()
                if email and document_path:
                    dsm.sign_document(email, document_path)
                else:
                    print("Email and document path are required.")
                    
            elif choice == "4":
                dsm.list_certificates()
                email = input("\nEnter email address: ").strip()
                document_path = input("Enter original document path: ").strip()
                signature_path = input("Enter signature path (optional): ").strip()
                
                if email and document_path:
                    dsm.verify_signature(email, document_path, signature_path if signature_path else None)
                else:
                    print("Email and document path are required.")
                    
            elif choice == "5":
                dsm.list_signed_documents()
                signed_doc_path = input("\nEnter signed document path: ").strip()
                if signed_doc_path:
                    dsm.verify_signed_document(signed_doc_path)
                else:
                    print("Signed document path is required.")
                
            elif choice == "6":
                dsm.list_certificates()
                
            elif choice == "7":
                dsm.list_signatures()
                
            elif choice == "8":
                dsm.list_signed_documents()
                
            elif choice == "9":
                doc_path = input("Enter document path (default: sample.txt): ").strip()
                if not doc_path:
                    doc_path = "sample.txt"
                create_sample_document(doc_path)
                
            else:
                print("Invalid option. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()