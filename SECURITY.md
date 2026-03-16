# 🔒 BotBot Security Guide

## Security Checklist for Production Deployment

### ⚠️ Critical Security Issues

Before deploying to production, **you MUST fix these security issues**:

### 1. Authentication & Authorization

✅ **Fixed Issues:**
- ✅ Direct login endpoint disabled (bypassed verification code)
- ✅ Rate limiting on verification code attempts (max 5 failed attempts)
- ✅ Generic error messages to prevent information leakage
- ✅ ObjectId validation with proper error handling
- ✅ Failed login attempt tracking

⚠️ **Manual Configuration Required:**

#### Change Default Secrets
```bash
# Generate strong random secrets (minimum 32 characters)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Update .env file
SECRET_KEY=<your-generated-secret>
JWT_SECRET_KEY=<your-generated-secret>
```

**DO NOT** use the example secrets in production:
- `your-secret-key-change-this-in-production` ❌
- `your-jwt-secret-key-change-this` ❌

### 2. Environment Configuration

#### Disable DEBUG Mode
```bash
# In production .env
DEBUG=False
```

When DEBUG=True:
- Detailed error messages are exposed
- Stack traces are visible to users
- Performance is degraded

#### Configure CORS Properly
```bash
# Development (allow all)
CORS_ORIGINS=*

# Production (restrict to your domains)
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

**Never use `CORS_ORIGINS=*` in production!**

### 3. Database Security

#### MongoDB Authentication
```bash
# Use authenticated MongoDB connection
MONGODB_URL=mongodb://username:password@host:27017/botbot?authSource=admin

# Enable SSL/TLS for production
MONGODB_URL=mongodb://username:password@host:27017/botbot?ssl=true&authSource=admin
```

#### Default Configuration ❌
```bash
# DO NOT use in production:
MONGODB_URL=mongodb://localhost:27017
```

### 4. API Security

#### Rate Limiting
Currently configured: 100 requests/minute per IP

For production, consider:
- Implementing Redis-based distributed rate limiting
- Different limits for different endpoints
- Lower limits for authentication endpoints (10/minute)

#### Input Validation
All endpoints use Pydantic validation, but ensure:
- Phone number format validation
- Amount range validation (min/max)
- String length limits

### 5. Payment Security

✅ **Already Implemented:**
- ✅ Signature verification for all payment callbacks
- ✅ Amount validation (0.01 RMB tolerance)
- ✅ Idempotency checks (prevent duplicate payments)
- ✅ MongoDB transactions for atomicity
- ✅ Dual approval for platform withdrawals

⚠️ **Configure Payment Credentials Securely:**
```bash
# Store private keys in secure files with restricted permissions
chmod 600 /path/to/alipay_private_key.pem
chmod 600 /path/to/wechat_apiclient_key.pem

# Never commit private keys to version control
# Add to .gitignore:
*.pem
*.key
alipay_private_key.pem
wechat_apiclient_*.pem
```

### 6. SMS Service

⚠️ **Current Behavior:**
- In DEBUG mode: Uses mock SMS (prints code to console)
- In production: Requires valid Aliyun credentials

**Never log verification codes in production!**

Remove or comment out debugging prints:
```python
# DEBUG ONLY - remove in production
print(f"Verification code: {code}")  # ❌ Remove this
```

### 7. Admin Security

✅ **Already Implemented:**
- ✅ Role-based access control (admin/user)
- ✅ Super admin initialization from environment
- ✅ Operation audit logging
- ✅ Dual approval for platform withdrawals

⚠️ **Best Practices:**
```bash
# Protect super admin phone number
SUPER_ADMIN_PHONE=<keep this secret>

# Use a dedicated admin phone number
# Don't use your personal phone
```

### 8. HTTPS/TLS

**Required for production:**
- All API endpoints must use HTTPS
- Configure reverse proxy (nginx/Apache) with SSL certificates
- Use Let's Encrypt for free SSL certificates
- Enable HSTS (HTTP Strict Transport Security)

Example nginx configuration:
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    # Strong SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Vulnerabilities Found & Fixed

### 🚨 Critical (Fixed)

1. **Direct Login Bypass** - `FIXED`
   - Endpoint `/auth/direct-login` allowed login without verification
   - Status: Disabled and commented out
   - Impact: Prevented unauthorized account access

2. **Insufficient Rate Limiting** - `FIXED`
   - Verification codes had no attempt limit
   - Status: Added 5 attempts limit with counter reset on new code
   - Impact: Prevented brute force attacks

### ⚠️ High (Mitigated)

3. **Error Information Leakage** - `FIXED`
   - Detailed error messages exposed internal information
   - Status: Generic error messages for authentication failures
   - Impact: Reduced attack surface

4. **ObjectId Validation** - `FIXED`
   - Empty except blocks hiding validation errors
   - Status: Proper exception handling with logging
   - Impact: Better error handling and debugging

## Monitoring & Logging

### Security Events to Monitor

1. **Authentication Events:**
   - Failed login attempts (>3 in 5 minutes)
   - Multiple verification code requests from same IP
   - Admin role changes

2. **Payment Events:**
   - Large withdrawal requests (>10,000 RMB)
   - Failed payment callback verifications
   - Duplicate transaction attempts

3. **Database Events:**
   - Failed MongoDB authentication
   - Slow queries (>1 second)
   - Connection pool exhaustion

### Log Rotation

Configure log rotation for production:
```bash
# /etc/logrotate.d/botbot
/var/log/botbot/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload botbot
    endscript
}
```

## Security Headers

Add these headers to your FastAPI application:

```python
# In app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Production only
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

## Backup & Disaster Recovery

### Database Backups
```bash
# Daily MongoDB backup
mongodump --uri="mongodb://user:pass@host/botbot" --out=/backup/$(date +%Y%m%d)

# Encrypt backup
tar czf - /backup/$(date +%Y%m%d) | openssl enc -aes-256-cbc -salt -out backup.tar.gz.enc

# Upload to secure storage (S3, etc.)
aws s3 cp backup.tar.gz.enc s3://your-backup-bucket/
```

### Private Key Backups
- Store payment private keys in secure vault (HashiCorp Vault, AWS Secrets Manager)
- Never store in version control
- Rotate keys annually

## Incident Response Plan

If you detect a security incident:

1. **Immediately:**
   - Disable affected endpoints if necessary
   - Revoke compromised tokens/credentials
   - Block suspicious IP addresses

2. **Investigate:**
   - Check audit logs for unauthorized access
   - Review transaction logs for fraudulent activity
   - Identify scope and impact

3. **Remediate:**
   - Patch vulnerabilities
   - Reset compromised credentials
   - Notify affected users if data breach occurred

4. **Post-Incident:**
   - Update security measures
   - Document incident and response
   - Review and improve security procedures

## Security Contacts

- Report security vulnerabilities: security@yourdomain.com
- For critical issues, include "SECURITY" in subject line

## Compliance

### GDPR Considerations (if operating in EU)
- User data retention policy
- Right to be forgotten implementation
- Data export functionality
- Privacy policy

### PCI-DSS (if handling card payments)
- Never store full card numbers
- Use tokenization for recurring payments
- Annual security audits required

## Regular Security Tasks

### Monthly:
- [ ] Review admin operation logs
- [ ] Check for suspicious login patterns
- [ ] Update dependencies (pip, npm)
- [ ] Review API access patterns

### Quarterly:
- [ ] Rotate JWT secrets
- [ ] Update SSL certificates
- [ ] Review user permissions
- [ ] Penetration testing

### Annually:
- [ ] Full security audit
- [ ] Rotate payment keys
- [ ] Review disaster recovery plan
- [ ] Update security documentation

---

**Last Updated:** 2026-03-16

**Security Team:** Contact security@yourdomain.com for questions or to report vulnerabilities.
