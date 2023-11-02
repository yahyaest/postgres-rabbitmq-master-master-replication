from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def generate_base64_csr(cn, key_file_path):
    # Generate an RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Serialize the private key to PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(key_file_path,"+w") as file:
        file.write(private_key_pem.decode('utf-8'))
    
    # Create a subject for the CSR with the provided CN
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, cn)
    ])
    
    # Create a CSR (Certificate Signing Request)
    csr = x509.CertificateSigningRequestBuilder().subject_name(
        subject
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    ).sign(private_key, hashes.SHA256())

    # Serialize the CSR to PEM format
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    
    # Encode the CSR in base64
    base64_csr = csr_pem.decode('utf-8')
    
    return base64_csr

def generate_certificate_from_csr(csr_pem, private_key_pem, cert_path):
    # Load the private key from the PEM format
    private_key = serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
    
    # Load the CSR from the PEM format
    csr = x509.load_pem_x509_csr(csr_pem.encode('utf-8'))
    
    # Create a self-signed certificate
    certificate = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        csr.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime(2023, 1, 1)
    ).not_valid_after(
        datetime(2025, 1, 1)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    ).sign(private_key, hashes.SHA256())
    
    # Serialize the certificate to PEM format
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)
    
    # Save the certificate to a file
    with open(cert_path, "+w") as cert_file:
        cert_file.write(certificate_pem.decode('utf-8'))
    
    return certificate_pem.decode('utf-8')

def get_certificate_attributes(cert_pem_base64):
    # Load the certificate from the PEM format
    cert = x509.load_pem_x509_certificate(cert_pem_base64.encode('utf-8'))
    
    # Retrieve certificate attributes
    common_name = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    serial_number = cert.serial_number
    fingerprint = cert.fingerprint(hashes.SHA256()).hex()
    expiration_date = cert.not_valid_after
    return {
        "CommonName": common_name,
        "SerialNumber": serial_number,
        "Fingerprint": fingerprint,
        "ExpirationDate": expiration_date
    }

if __name__ == "__main__":
    owner= "yahya"
    cn = "yahya"
    key_file_path = f"keys/{cn}.key"
    cert_path = f"certs/{cn}.pem"

    # Generate CSR
    base64_csr = generate_base64_csr(cn, key_file_path)
    print("Base64 CSR:")
    print(base64_csr)

    # Load CSR and private key
    with open(key_file_path, "r") as key_file:
        private_key_pem = key_file.read()
    
    print("Base64 Key:")
    print(private_key_pem)

    # Generate and save the certificate
    base64_cert = generate_certificate_from_csr(base64_csr, private_key_pem, cert_path)
    print("Base64 Certificate:")
    print(base64_cert)

    certificate_attributes = get_certificate_attributes(base64_cert)
    
    print("Certificate Attributes:")
    for key, value in certificate_attributes.items():
        if isinstance(value, datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{key}: {value}")
    

    
    connection = psycopg2.connect(
    dbname="crypto",
    user="postgres",
    password="postgres",
    host="postgres",
    port="5432"
    )

    ### Postgres 
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    # register a LISTEN command
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO certificates (owner, common_name, serial_number, fingerprint, cert_b64, expiration_date)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (owner, certificate_attributes["CommonName"], certificate_attributes["SerialNumber"],
        certificate_attributes["Fingerprint"], cert_path, certificate_attributes["ExpirationDate"]))
    
    # cursor.execute("""
    #     INSERT INTO certificates (owner, common_name, serial_number, fingerprint, cert_b64, expiration_date)
    #     VALUES (%s, %s, %s, %s, %s, %s);
    # """, (owner, certificate_attributes["CommonName"], certificate_attributes["SerialNumber"],
    #     certificate_attributes["Fingerprint"], base64_cert, certificate_attributes["ExpirationDate"]))
    

    