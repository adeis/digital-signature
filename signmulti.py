import os
import sys
import hashlib
import datetime
import argparse
import json
import uuid
from pathlib import Path
from enum import Enum
from typing import List, Dict, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import (
    Name, NameAttribute, NameOID, CertificateBuilder, load_pem_x509_certificate
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red, black, blue
from reportlab.lib.units import inch
from PyPDF2 import PdfReader, PdfWriter
import io

class SigningMode(Enum):
    """Mode penandatanganan multi-signature"""
    SEQUENTIAL = "sequential"  # Berurutan - harus sesuai urutan
    INDEPENDENT = "independent"  # Paralel - bisa sign kapan saja
    HYBRID = "hybrid"  # Kombinasi - ada tahapan berurutan dan paralel

class SigningStatus(Enum):
    """Status penandatanganan"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MultiSignatureManager:
    def __init__(self):
        self.root_ca_cert_path = "rootca.crt"
        self.root_ca_key_path = "rootca.key"
        self.certs_dir = "certificates"
        self.signatures_dir = "signatures"
        self.multisig_dir = "multisignatures"
        
        # Buat direktori jika belum ada
        Path(self.certs_dir).mkdir(exist_ok=True)
        Path(self.signatures_dir).mkdir(exist_ok=True)
        Path(self.multisig_dir).mkdir(exist_ok=True)

    def create_root_ca(self, force=False):
        """Membuat Root CA (sama seperti single signature)"""
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
            NameAttribute(NameOID.ORGANIZATION_NAME, u"Multi-Signature Root CA"),
            NameAttribute(NameOID.COMMON_NAME, u"Multi-Signature Root CA"),
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
            NameAttribute(NameOID.ORGANIZATION_NAME, u"Multi-Signature User"),
            NameAttribute(NameOID.COMMON_NAME, email),
            NameAttribute(NameOID.EMAIL_ADDRESS, email),
        ])

        user_cert_builder = (
            CertificateBuilder()
            .subject_name(user_subject)
            .issuer_name(ca_cert.subject)
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .serial_number(hash(email) % (2**32))
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

    def create_multisig_session(self, document_path: str, required_signers: List[str], 
                               signing_mode: SigningMode = SigningMode.SEQUENTIAL,
                               session_name: str = None, roles: Dict[str, str] = None):
        """Membuat session multi-signature baru"""
        if not os.path.exists(document_path):
            print(f"Document {document_path} not found.")
            return None

        # Generate session ID
        session_id = str(uuid.uuid4())[:8]
        if session_name:
            session_id = f"{session_name}_{session_id}"

        # Buat direktori session
        session_dir = os.path.join(self.multisig_dir, session_id)
        Path(session_dir).mkdir(exist_ok=True)
        
        signatures_dir = os.path.join(session_dir, "signatures")
        Path(signatures_dir).mkdir(exist_ok=True)

        # Copy dokumen asli ke session directory
        doc_name = Path(document_path).name
        session_doc_path = os.path.join(session_dir, f"original_{doc_name}")
        
        with open(document_path, "rb") as src, open(session_doc_path, "wb") as dst:
            dst.write(src.read())

        # Hitung hash dokumen
        with open(document_path, "rb") as f:
            document_data = f.read()
        document_hash = hashlib.sha256(document_data).hexdigest()

        # Buat metadata session
        session_metadata = {
            "session_id": session_id,
            "session_name": session_name or f"MultiSig_{session_id}",
            "document_path": document_path,
            "document_name": doc_name,
            "session_document_path": session_doc_path,
            "document_hash_sha256": document_hash,
            "signing_mode": signing_mode.value,
            "required_signers": required_signers,
            "roles": roles or {},
            "signatures": [],
            "status": SigningStatus.PENDING.value,
            "created_on": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "completed_on": None,
            "current_signer_index": 0 if signing_mode == SigningMode.SEQUENTIAL else -1
        }

        # Simpan metadata
        metadata_path = os.path.join(session_dir, "session_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(session_metadata, f, indent=2)

        print(f"✅ Multi-signature session created!")
        print(f"Session ID: {session_id}")
        print(f"Document: {doc_name}")
        print(f"Signing mode: {signing_mode.value}")
        print(f"Required signers: {', '.join(required_signers)}")
        print(f"Session directory: {session_dir}")
        
        return session_id

    def _find_session_by_id_or_name(self, search_term: str):
        """Cari session berdasarkan ID atau name"""
        if not os.path.exists(self.multisig_dir):
            return None
            
        sessions = [d for d in os.listdir(self.multisig_dir) 
                   if os.path.isdir(os.path.join(self.multisig_dir, d))]
        
        # First try exact ID match
        if search_term in sessions:
            return search_term
            
        # Then try to find by session name
        for session_id in sessions:
            metadata_path = os.path.join(self.multisig_dir, session_id, "session_metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    if metadata.get("session_name") == search_term:
                        return session_id
                except:
                    continue
        
        return None

    def sign_document_in_session(self, session_id: str, signer_email: str):
        """Menandatangani dokumen dalam session multi-signature"""
        # Try to find session by ID or name
        actual_session_id = self._find_session_by_id_or_name(session_id)
        if not actual_session_id:
            print(f"❌ Session '{session_id}' not found.")
            return False
            
        session_dir = os.path.join(self.multisig_dir, actual_session_id)
        metadata_path = os.path.join(session_dir, "session_metadata.json")

        # Load metadata session
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Validasi signer
        if signer_email not in metadata["required_signers"]:
            print(f"❌ {signer_email} is not a required signer for this session.")
            return False

        # Cek apakah sudah sign
        existing_signatures = [sig["signer"] for sig in metadata["signatures"]]
        if signer_email in existing_signatures:
            print(f"⚠️  {signer_email} has already signed this document.")
            return False

        # Validasi mode sequential
        if metadata["signing_mode"] == SigningMode.SEQUENTIAL.value:
            current_index = metadata["current_signer_index"]
            expected_signer = metadata["required_signers"][current_index]
            if signer_email != expected_signer:
                print(f"❌ Sequential signing mode: Expected {expected_signer}, got {signer_email}")
                print(f"   Current signing order: {current_index + 1} of {len(metadata['required_signers'])}")
                return False

        # Validasi sertifikat pengguna
        user_key_path = os.path.join(self.certs_dir, f"{signer_email}.key")
        user_cert_path = os.path.join(self.certs_dir, f"{signer_email}.crt")

        if not os.path.exists(user_key_path) or not os.path.exists(user_cert_path):
            print(f"❌ Certificate for {signer_email} not found. Please create user certificate first.")
            return False

        # Load user private key
        with open(user_key_path, "rb") as f:
            user_private_key = serialization.load_pem_private_key(f.read(), password=None)

        # Read original document
        original_doc_path = metadata["session_document_path"]
        with open(original_doc_path, "rb") as f:
            document_data = f.read()

        # Verify document integrity
        current_hash = hashlib.sha256(document_data).hexdigest()
        if current_hash != metadata["document_hash_sha256"]:
            print(f"❌ Document integrity check failed! Document may have been tampered with.")
            return False

        # Create document hash and sign
        document_hash = hashlib.sha256(document_data).digest()
        signature = user_private_key.sign(
            document_hash,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Save signature
        signatures_dir = os.path.join(session_dir, "signatures")
        signature_path = os.path.join(signatures_dir, f"{signer_email}.sig")
        
        with open(signature_path, "wb") as f:
            f.write(signature)

        # Update metadata
        sign_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        signature_info = {
            "signer": signer_email,
            "signed_on": sign_time,
            "signature_file": signature_path,
            "signature_order": len(metadata["signatures"]) + 1,
            "role": metadata["roles"].get(signer_email, "Signer")
        }
        
        metadata["signatures"].append(signature_info)
        
        # Update status dan current signer index
        if metadata["signing_mode"] == SigningMode.SEQUENTIAL.value:
            metadata["current_signer_index"] += 1
            
        # Cek apakah semua sudah sign
        if len(metadata["signatures"]) == len(metadata["required_signers"]):
            metadata["status"] = SigningStatus.COMPLETED.value
            metadata["completed_on"] = sign_time
        else:
            metadata["status"] = SigningStatus.IN_PROGRESS.value

        # Save updated metadata
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Document signed successfully by {signer_email}!")
        print(f"   Signature order: {signature_info['signature_order']} of {len(metadata['required_signers'])}")
        print(f"   Role: {signature_info['role']}")
        print(f"   Signed on: {sign_time}")
        
        if metadata["status"] == SigningStatus.COMPLETED.value:
            print(f"🎉 All signatures collected! Session completed.")
            return self._finalize_multisig_document(session_id)
        else:
            remaining = len(metadata["required_signers"]) - len(metadata["signatures"])
            print(f"   Remaining signatures needed: {remaining}")
            
            if metadata["signing_mode"] == SigningMode.SEQUENTIAL.value:
                next_signer_index = metadata["current_signer_index"]
                if next_signer_index < len(metadata["required_signers"]):
                    next_signer = metadata["required_signers"][next_signer_index]
                    print(f"   Next signer (sequential): {next_signer}")

        return True

    def _finalize_multisig_document(self, session_id: str):
        """Finalisasi dokumen multi-signature dengan semua tanda tangan"""
        session_dir = os.path.join(self.multisig_dir, session_id)
        metadata_path = os.path.join(session_dir, "session_metadata.json")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Create final signed document
        original_doc_path = metadata["session_document_path"]
        doc_name = Path(metadata["document_name"]).stem
        doc_ext = Path(metadata["document_name"]).suffix
        
        final_doc_path = os.path.join(session_dir, f"final_multisigned_{doc_name}{doc_ext}")

        try:
            if doc_ext.lower() == '.pdf':
                self._create_multisig_pdf(original_doc_path, final_doc_path, metadata)
            else:
                self._create_multisig_text_pdf(original_doc_path, final_doc_path, metadata)
                
            print(f"📄 Final multi-signed document created: {final_doc_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating final document: {e}")
            return False

    def _create_multisig_pdf(self, original_pdf_path, final_pdf_path, metadata):
        """Buat PDF final dengan watermark multi-signature"""
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()
        
        # Create watermark with all signatures
        watermark_buffer = io.BytesIO()
        c = canvas.Canvas(watermark_buffer, pagesize=letter)
        
        # Header watermark
        c.setFillColor(red, alpha=0.3)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 750, f"MULTI-SIGNATURE DOCUMENT")
        
        c.setFillColor(blue, alpha=0.4)
        c.setFont("Helvetica", 8)
        c.drawString(50, 735, f"Session: {metadata['session_name']}")
        c.drawString(50, 725, f"Mode: {metadata['signing_mode'].upper()}")
        c.drawString(50, 715, f"Completed: {metadata['completed_on']}")
        
        # Signatures info
        y_pos = 690
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y_pos, "SIGNERS:")
        
        for i, sig in enumerate(metadata["signatures"]):
            y_pos -= 15
            c.setFont("Helvetica", 8)
            role = sig.get('role', 'Signer')
            c.drawString(60, y_pos, f"{i+1}. {sig['signer']} ({role}) - {sig['signed_on']}")
        
        c.save()
        watermark_buffer.seek(0)
        
        # Apply watermark to all pages
        watermark_pdf = PdfReader(watermark_buffer)
        watermark_page = watermark_pdf.pages[0]
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        # Add metadata
        writer.add_metadata({
            '/Title': f'Multi-Signed Document - {metadata["document_name"]}',
            '/Author': f'Multi-Signature System',
            '/Subject': f'Document signed by {len(metadata["signatures"])} parties',
            '/Creator': 'Multi-Signature Manager',
            '/Producer': 'Multi-Signature Manager'
        })
        
        with open(final_pdf_path, "wb") as output_file:
            writer.write(output_file)

    def _create_multisig_text_pdf(self, original_file_path, final_pdf_path, metadata):
        """Buat PDF dari file teks dengan info multi-signature"""
        c = canvas.Canvas(final_pdf_path, pagesize=letter)
        
        # Header
        c.setFillColor(red)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "MULTI-SIGNATURE DOCUMENT")
        
        c.setFillColor(black)
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, f"Session: {metadata['session_name']}")
        c.drawString(100, 705, f"Original: {metadata['document_name']}")
        c.drawString(100, 690, f"Signing Mode: {metadata['signing_mode'].upper()}")
        c.drawString(100, 675, f"Completed: {metadata['completed_on']}")
        
        # Signatures section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 650, "SIGNATURES:")
        
        y_pos = 630
        for i, sig in enumerate(metadata["signatures"]):
            c.setFont("Helvetica", 10)
            role = sig.get('role', 'Signer')
            c.drawString(120, y_pos, f"{i+1}. {sig['signer']} ({role})")
            c.drawString(140, y_pos-12, f"Signed on: {sig['signed_on']}")
            y_pos -= 30
        
        # Separator
        c.line(100, y_pos-10, 500, y_pos-10)
        y_pos -= 30
        
        # Original content
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_pos, "ORIGINAL DOCUMENT CONTENT:")
        y_pos -= 20
        
        try:
            with open(original_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            c.setFont("Helvetica", 9)
            line_height = 12
            max_chars_per_line = 80
            
            for line in content.split('\n'):
                if y_pos < 50:
                    c.showPage()
                    y_pos = 750
                
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
            c.drawString(120, y_pos, f"Error reading original file: {e}")
        
        c.save()

    def verify_multisig_session(self, session_id: str):
        """Verifikasi semua tanda tangan dalam session multi-signature"""
        # Try to find session by ID or name
        actual_session_id = self._find_session_by_id_or_name(session_id)
        if not actual_session_id:
            print(f"❌ Session '{session_id}' not found.")
            return False
            
        session_dir = os.path.join(self.multisig_dir, actual_session_id)
        metadata_path = os.path.join(session_dir, "session_metadata.json")

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        print(f"\n🔍 MULTI-SIGNATURE VERIFICATION")
        print(f"=" * 50)
        print(f"Session: {metadata['session_name']}")
        print(f"Document: {metadata['document_name']}")
        print(f"Signing Mode: {metadata['signing_mode'].upper()}")
        print(f"Status: {metadata['status'].upper()}")
        print(f"Required Signers: {len(metadata['required_signers'])}")
        print(f"Collected Signatures: {len(metadata['signatures'])}")

        # Verify document integrity
        original_doc_path = metadata["session_document_path"]
        if not os.path.exists(original_doc_path):
            print(f"❌ Original document not found: {original_doc_path}")
            return False

        with open(original_doc_path, "rb") as f:
            document_data = f.read()
        
        current_hash = hashlib.sha256(document_data).hexdigest()
        if current_hash != metadata["document_hash_sha256"]:
            print(f"❌ Document integrity check FAILED!")
            print(f"   Expected: {metadata['document_hash_sha256']}")
            print(f"   Current:  {current_hash}")
            return False
        
        print(f"✅ Document integrity check PASSED")

        # Verify each signature
        all_valid = True
        document_hash = hashlib.sha256(document_data).digest()
        
        print(f"\n📋 SIGNATURE VERIFICATION:")
        for i, sig_info in enumerate(metadata["signatures"]):
            signer = sig_info["signer"]
            signature_file = sig_info["signature_file"]
            
            print(f"\n{i+1}. Verifying {signer}...")
            
            # Load certificate and signature
            user_cert_path = os.path.join(self.certs_dir, f"{signer}.crt")
            
            if not os.path.exists(user_cert_path):
                print(f"   ❌ Certificate not found: {user_cert_path}")
                all_valid = False
                continue
                
            if not os.path.exists(signature_file):
                print(f"   ❌ Signature file not found: {signature_file}")
                all_valid = False
                continue

            try:
                # Load certificate and signature
                with open(user_cert_path, "rb") as f:
                    user_cert = load_pem_x509_certificate(f.read())
                
                with open(signature_file, "rb") as f:
                    signature = f.read()

                # Verify signature
                public_key = user_cert.public_key()
                public_key.verify(
                    signature,
                    document_hash,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                
                role = sig_info.get('role', 'Signer')
                print(f"   ✅ VALID - {signer} ({role}) - {sig_info['signed_on']}")
                
            except Exception as e:
                print(f"   ❌ INVALID - {signer}: {e}")
                all_valid = False

        print(f"\n" + "=" * 50)
        if all_valid and len(metadata["signatures"]) == len(metadata["required_signers"]):
            print(f"🎉 MULTI-SIGNATURE VERIFICATION SUCCESSFUL!")
            print(f"✅ All {len(metadata['signatures'])} signatures are VALID and AUTHENTIC")
            print(f"✅ Document integrity confirmed")
            print(f"✅ All required signers have signed")
            return True
        else:
            print(f"❌ MULTI-SIGNATURE VERIFICATION FAILED!")
            if not all_valid:
                print(f"   Some signatures are invalid")
            if len(metadata["signatures"]) != len(metadata["required_signers"]):
                print(f"   Missing signatures: {len(metadata['required_signers']) - len(metadata['signatures'])}")
            return False

    def list_multisig_sessions(self):
        """List semua session multi-signature"""
        print("\n=== Multi-Signature Sessions ===")
        
        if not os.path.exists(self.multisig_dir):
            print("No multi-signature sessions found.")
            return
            
        sessions = [d for d in os.listdir(self.multisig_dir) 
                   if os.path.isdir(os.path.join(self.multisig_dir, d))]
        
        if not sessions:
            print("No multi-signature sessions found.")
            return
            
        for session_id in sessions:
            metadata_path = os.path.join(self.multisig_dir, session_id, "session_metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    
                    status_icon = {
                        "pending": "⏳",
                        "in_progress": "🔄", 
                        "completed": "✅",
                        "cancelled": "❌"
                    }.get(metadata["status"], "❓")
                    
                    print(f"\n{status_icon} {session_id}")
                    print(f"   Name: {metadata['session_name']}")
                    print(f"   Document: {metadata['document_name']}")
                    print(f"   Mode: {metadata['signing_mode'].upper()}")
                    print(f"   Status: {metadata['status'].upper()}")
                    print(f"   Signatures: {len(metadata['signatures'])}/{len(metadata['required_signers'])}")
                    print(f"   Created: {metadata['created_on']}")
                    
                    if metadata["status"] == "completed":
                        print(f"   Completed: {metadata['completed_on']}")
                    elif metadata["status"] == "in_progress":
                        if metadata["signing_mode"] == "sequential":
                            current_index = metadata.get("current_signer_index", 0)
                            if current_index < len(metadata["required_signers"]):
                                next_signer = metadata["required_signers"][current_index]
                                print(f"   Next signer: {next_signer}")
                        
                except Exception as e:
                    print(f"   ❌ Error reading session {session_id}: {e}")

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

def create_sample_document(path):
    """Membuat dokumen contoh untuk testing multi-signature"""
    content = f"""MULTI-SIGNATURE CONTRACT

Contract ID: MSC-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}
Date: {datetime.datetime.now().strftime('%Y-%m-%d')}

PARTIES:
This contract is between multiple parties who must all sign to make it valid.

TERMS:
1. All parties must review and sign this document
2. Sequential signing may be required depending on roles
3. Document integrity must be maintained throughout the process
4. Digital signatures provide legal authenticity

SIGNATURE REQUIREMENTS:
- Manager: Must sign first (if sequential mode)
- Department Heads: Can sign in any order (if independent mode)
- Legal Counsel: Final approval (if sequential mode)

This document demonstrates multi-signature digital signing capabilities.

Created on: {datetime.datetime.now()}
"""
    
    with open(path, "w") as f:
        f.write(content)
    print(f"Sample multi-signature document created: {path}")

def main():
    msm = MultiSignatureManager()
    
    if len(sys.argv) > 1:
        # Command line mode
        parser = argparse.ArgumentParser(description='Multi-Signature Manager')
        parser.add_argument('--force', action='store_true', help='Force recreate Root CA')
        args = parser.parse_args()
        
        if args.force:
            msm.create_root_ca(force=True)
            return
    
    # Interactive mode
    while True:
        print("\n" + "="*60)
        print("    MULTI-SIGNATURE DIGITAL SIGNATURE MANAGER")
        print("="*60)
        print("1. Create Root CA")
        print("2. Create User Certificate") 
        print("3. Create Multi-Signature Session")
        print("4. Sign Document in Session")
        print("5. Verify Multi-Signature Session")
        print("6. List Multi-Signature Sessions")
        print("7. List Certificates")
        print("8. Create Sample Document")
        print("0. Exit")
        print("-"*60)
        
        try:
            choice = input("Select option (0-8): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
                
            elif choice == "1":
                force = input("Force recreate if exists? (y/N): ").strip().lower() == 'y'
                msm.create_root_ca(force=force)
                
            elif choice == "2":
                email = input("Enter email address: ").strip()
                if email:
                    msm.create_user_certificate(email)
                else:
                    print("Email address is required.")
                    
            elif choice == "3":
                print("\nCreating Multi-Signature Session...")
                document_path = input("Enter document path: ").strip()
                if not document_path:
                    print("Document path is required.")
                    continue
                    
                signers_input = input("Enter required signers (comma-separated emails): ").strip()
                if not signers_input:
                    print("At least one signer is required.")
                    continue
                    
                required_signers = [email.strip() for email in signers_input.split(",")]
                
                print("\nSigning modes:")
                print("1. Sequential (berurutan)")
                print("2. Independent (paralel)")
                print("3. Hybrid (kombinasi)")
                
                mode_choice = input("Select signing mode (1-3): ").strip()
                mode_map = {
                    "1": SigningMode.SEQUENTIAL,
                    "2": SigningMode.INDEPENDENT, 
                    "3": SigningMode.HYBRID
                }
                
                signing_mode = mode_map.get(mode_choice, SigningMode.SEQUENTIAL)
                session_name = input("Enter session name (optional): ").strip() or None
                
                # Optional: roles
                roles = {}
                if input("Add roles for signers? (y/N): ").strip().lower() == 'y':
                    for signer in required_signers:
                        role = input(f"Role for {signer} (optional): ").strip()
                        if role:
                            roles[signer] = role
                
                session_id = msm.create_multisig_session(
                    document_path, required_signers, signing_mode, session_name, roles
                )
                
            elif choice == "4":
                msm.list_multisig_sessions()
                session_id = input("\nEnter session ID: ").strip()
                signer_email = input("Enter signer email: ").strip()
                
                if session_id and signer_email:
                    msm.sign_document_in_session(session_id, signer_email)
                else:
                    print("Session ID and signer email are required.")
                    
            elif choice == "5":
                msm.list_multisig_sessions()
                session_id = input("\nEnter session ID to verify: ").strip()
                if session_id:
                    msm.verify_multisig_session(session_id)
                else:
                    print("Session ID is required.")
                
            elif choice == "6":
                msm.list_multisig_sessions()
                
            elif choice == "7":
                msm.list_certificates()
                
            elif choice == "8":
                doc_path = input("Enter document path (default: multisig_contract.txt): ").strip()
                if not doc_path:
                    doc_path = "multisig_contract.txt"
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