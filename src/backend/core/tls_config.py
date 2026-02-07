"""
TLS/HTTPS configuration for production deployment.
Implements NCA CCC-SEC-03 requirements.
"""
import ssl
import os


def get_ssl_context():
    """
    Create SSL context for HTTPS.
    In production, use certificates from Azure Key Vault or Let's Encrypt.
    """
    from core.config import settings
    
    if not settings.TLS_ENABLED:
        return None
    
    # Create SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # Load certificate and private key
    if os.path.exists(settings.TLS_CERT_PATH) and os.path.exists(settings.TLS_KEY_PATH):
        ssl_context.load_cert_chain(
            certfile=settings.TLS_CERT_PATH,
            keyfile=settings.TLS_KEY_PATH
        )
    else:
        # Development: Generate self-signed certificate
        # WARNING: Do not use in production
        print("⚠️  TLS certificates not found. Using development mode (HTTP only).")
        print("   For production, configure TLS_CERT_PATH and TLS_KEY_PATH in settings.")
        return None
    
    # Security settings (NCA CCC recommendations)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2  # Minimum TLS 1.2
    ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
    
    return ssl_context


def generate_self_signed_cert(cert_path: str, key_path: str):
    """
    Generate self-signed certificate for development.
    DO NOT use in production - use Let's Encrypt or Azure certificates.
    """
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from datetime import datetime, timedelta
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "SA"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Riyadh"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Riyadh"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SICO GRC Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write private key
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print(f"✓ Generated self-signed certificate: {cert_path}")
    print(f"✓ Generated private key: {key_path}")
    print("⚠️  WARNING: Self-signed certificates are for development only!")


# Docker Compose configuration for TLS
DOCKER_COMPOSE_TLS = """
# Add to docker-compose.yml for TLS support
services:
  backend:
    environment:
      - TLS_ENABLED=true
      - TLS_CERT_PATH=/etc/ssl/certs/server.crt
      - TLS_KEY_PATH=/etc/ssl/private/server.key
    volumes:
      - ./certs/server.crt:/etc/ssl/certs/server.crt:ro
      - ./certs/server.key:/etc/ssl/private/server.key:ro
    ports:
      - "443:443"  # HTTPS
      - "8000:8000"  # HTTP (redirect to HTTPS)
"""


# Nginx reverse proxy configuration for production
NGINX_CONFIG = """
# /etc/nginx/sites-available/sico-grc
server {
    listen 80;
    server_name sico-grc.com www.sico-grc.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sico-grc.com www.sico-grc.com;

    # TLS certificates (Let's Encrypt or Azure)
    ssl_certificate /etc/letsencrypt/live/sico-grc.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sico-grc.com/privkey.pem;

    # TLS settings (NCA CCC-SEC-03 compliant)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Proxy to FastAPI backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy to Next.js frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
