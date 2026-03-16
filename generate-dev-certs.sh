#!/bin/bash
# Generate self-signed SSL certificates for local development
# This script creates certificates for botbot.biz domain

set -e

CERTS_DIR="nginx/certs"
DOMAIN="botbot.biz"
DAYS=365

echo "🔐 Generating SSL certificates for BotBot"
echo "=========================================="
echo ""

# Create certs directory if not exists
mkdir -p "$CERTS_DIR"

# Check if certificates already exist
if [ -f "$CERTS_DIR/$DOMAIN.crt" ] && [ -f "$CERTS_DIR/$DOMAIN.key" ]; then
    echo "⚠️  Certificates already exist!"
    echo ""
    echo "Existing certificates:"
    ls -lh "$CERTS_DIR/$DOMAIN.crt" "$CERTS_DIR/$DOMAIN.key"
    echo ""

    # Check expiry date
    echo "Certificate expiry date:"
    openssl x509 -in "$CERTS_DIR/$DOMAIN.crt" -noout -enddate
    echo ""

    read -p "Do you want to regenerate certificates? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled. Using existing certificates."
        exit 0
    fi

    echo "🗑️  Removing old certificates..."
    rm -f "$CERTS_DIR/$DOMAIN.crt" "$CERTS_DIR/$DOMAIN.key"
fi

echo "📝 Certificate configuration:"
echo "  Domain: $DOMAIN"
echo "  Valid for: $DAYS days"
echo "  Location: $CERTS_DIR/"
echo ""

# Generate private key and certificate
echo "🔑 Generating private key and self-signed certificate..."
openssl req -x509 -nodes -days $DAYS -newkey rsa:2048 \
  -keyout "$CERTS_DIR/$DOMAIN.key" \
  -out "$CERTS_DIR/$DOMAIN.crt" \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BotBot Development/OU=Development/CN=$DOMAIN" \
  -addext "subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN,DNS:localhost,IP:127.0.0.1"

echo "✅ Certificate and key generated successfully!"
echo ""

# Generate DH parameters (optional, improves security)
read -p "Generate DH parameters? (improves security, takes ~2 minutes) (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Generating DH parameters (this may take a few minutes)..."
    openssl dhparam -out "$CERTS_DIR/dhparam.pem" 2048
    echo "✅ DH parameters generated!"
    echo ""
fi

# Set proper file permissions
echo "🔒 Setting file permissions..."
chmod 600 "$CERTS_DIR/$DOMAIN.key"
chmod 644 "$CERTS_DIR/$DOMAIN.crt"
if [ -f "$CERTS_DIR/dhparam.pem" ]; then
    chmod 644 "$CERTS_DIR/dhparam.pem"
fi

echo "✅ Permissions set:"
ls -lh "$CERTS_DIR/" | grep -E "\.crt|\.key|\.pem"
echo ""

# Display certificate information
echo "📄 Certificate information:"
openssl x509 -in "$CERTS_DIR/$DOMAIN.crt" -noout -subject -issuer -dates
echo ""

# Verify certificate
echo "🔍 Verifying certificate and key match..."
CERT_MD5=$(openssl x509 -noout -modulus -in "$CERTS_DIR/$DOMAIN.crt" | openssl md5 | cut -d' ' -f2)
KEY_MD5=$(openssl rsa -noout -modulus -in "$CERTS_DIR/$DOMAIN.key" 2>/dev/null | openssl md5 | cut -d' ' -f2)

if [ "$CERT_MD5" = "$KEY_MD5" ]; then
    echo "✅ Certificate and key match!"
else
    echo "❌ Certificate and key do NOT match!"
    exit 1
fi
echo ""

echo "🎉 Certificate generation complete!"
echo ""
echo "📁 Generated files:"
echo "  • $CERTS_DIR/$DOMAIN.crt (certificate)"
echo "  • $CERTS_DIR/$DOMAIN.key (private key)"
if [ -f "$CERTS_DIR/dhparam.pem" ]; then
    echo "  • $CERTS_DIR/dhparam.pem (DH parameters)"
fi
echo ""

echo "⚠️  IMPORTANT: Self-signed certificates"
echo "=========================================="
echo "These certificates are for DEVELOPMENT ONLY."
echo "Browsers will show a security warning until you trust the certificate."
echo ""
echo "To trust the certificate on your system:"
echo ""
echo "macOS:"
echo "  sudo security add-trusted-cert -d -r trustRoot \\"
echo "    -k /Library/Keychains/System.keychain $CERTS_DIR/$DOMAIN.crt"
echo ""
echo "Linux (Ubuntu/Debian):"
echo "  sudo cp $CERTS_DIR/$DOMAIN.crt /usr/local/share/ca-certificates/"
echo "  sudo update-ca-certificates"
echo ""
echo "Linux (CentOS/RHEL):"
echo "  sudo cp $CERTS_DIR/$DOMAIN.crt /etc/pki/ca-trust/source/anchors/"
echo "  sudo update-ca-trust"
echo ""
echo "Windows:"
echo "  Double-click $CERTS_DIR/$DOMAIN.crt and install it to"
echo "  'Trusted Root Certification Authorities'"
echo ""

echo "Next steps:"
echo "  1. (Optional) Trust the certificate using the commands above"
echo "  2. Start the services: docker-compose up -d"
echo "  3. Access via HTTPS: https://botbot.biz"
echo ""
echo "For production, use a proper certificate from Let's Encrypt or a CA."
echo "See nginx/certs/README.md for details."
