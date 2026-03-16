"""Security Configuration Checks"""
import sys
from app.core.config import settings


def check_production_security():
    """
    Check security configuration and warn about unsafe settings
    Run on application startup
    """
    warnings = []
    errors = []

    # Check DEBUG mode
    if settings.DEBUG:
        warnings.append(
            "⚠️  DEBUG mode is enabled. This should be disabled in production.\n"
            "   Set DEBUG=False in your .env file."
        )

    # Check secret keys
    weak_secrets = [
        "your-secret-key-change-this-in-production",
        "your-jwt-secret-key-change-this",
        "secret",
        "changeme",
        "password",
        "12345"
    ]

    if settings.SECRET_KEY in weak_secrets or len(settings.SECRET_KEY) < 32:
        errors.append(
            "🚨 CRITICAL: SECRET_KEY is weak or using default value!\n"
            "   Generate a strong secret: openssl rand -hex 32\n"
            "   Update SECRET_KEY in your .env file."
        )

    if settings.JWT_SECRET_KEY in weak_secrets or len(settings.JWT_SECRET_KEY) < 32:
        errors.append(
            "🚨 CRITICAL: JWT_SECRET_KEY is weak or using default value!\n"
            "   Generate a strong secret: openssl rand -hex 32\n"
            "   Update JWT_SECRET_KEY in your .env file."
        )

    # Check CORS
    cors_origins = settings.get_cors_origins()
    if "*" in cors_origins and not settings.DEBUG:
        warnings.append(
            "⚠️  CORS is set to allow all origins (*) in production mode.\n"
            "   This is a security risk. Restrict CORS_ORIGINS to your domain(s)."
        )

    # Check MongoDB URL
    if "localhost" in settings.MONGODB_URL and not settings.DEBUG:
        warnings.append(
            "⚠️  MongoDB URL points to localhost in production mode.\n"
            "   Consider using a dedicated database server with authentication."
        )

    if "mongodb://" in settings.MONGODB_URL and ":@" not in settings.MONGODB_URL:
        warnings.append(
            "⚠️  MongoDB connection has no authentication.\n"
            "   Use authenticated connection: mongodb://user:pass@host/db"
        )

    # Check token expiration
    if settings.ACCESS_TOKEN_EXPIRE_MINUTES > 1440:  # More than 24 hours
        warnings.append(
            f"⚠️  ACCESS_TOKEN_EXPIRE_MINUTES is very long ({settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes).\n"
            "   Consider using shorter expiration for better security."
        )

    # Check payment configuration
    if not settings.DEBUG:
        if not settings.ALIPAY_APP_ID and not settings.WECHAT_APP_ID:
            warnings.append(
                "⚠️  No payment gateway configured (Alipay/WeChat).\n"
                "   Payment features will not work in production."
            )

    # Print warnings and errors
    if errors:
        print("\n" + "="*70)
        print("🚨 CRITICAL SECURITY ERRORS - APPLICATION STARTUP BLOCKED")
        print("="*70)
        for error in errors:
            print(f"\n{error}")
        print("\n" + "="*70)
        print("Please fix these critical security issues before starting the application.")
        print("See SECURITY.md for detailed security guidelines.")
        print("="*70 + "\n")
        sys.exit(1)

    if warnings:
        print("\n" + "="*70)
        print("⚠️  SECURITY WARNINGS")
        print("="*70)
        for warning in warnings:
            print(f"\n{warning}")
        print("\n" + "="*70)
        print("See SECURITY.md for detailed security guidelines.")
        print("="*70 + "\n")

    # Print security status
    if not warnings and not errors:
        print("✅ Security configuration check passed")


def validate_object_id(obj_id: str) -> bool:
    """
    Validate MongoDB ObjectId format

    Args:
        obj_id: String to validate

    Returns:
        True if valid ObjectId format, False otherwise
    """
    if not isinstance(obj_id, str):
        return False

    if len(obj_id) != 24:
        return False

    try:
        int(obj_id, 16)
        return True
    except ValueError:
        return False


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitize phone number for logging (mask middle digits)

    Args:
        phone: Phone number

    Returns:
        Masked phone number (e.g., 138****8000)
    """
    if not phone or len(phone) < 7:
        return "***"

    return f"{phone[:3]}****{phone[-4:]}"


def sanitize_error_message(error: Exception, debug: bool = False) -> str:
    """
    Sanitize error message to prevent information leakage

    Args:
        error: Exception object
        debug: Whether to return full error (for debugging)

    Returns:
        Safe error message
    """
    if debug:
        return str(error)

    # Generic error messages
    error_type = type(error).__name__

    safe_messages = {
        "ValueError": "Invalid input provided",
        "KeyError": "Required field missing",
        "TypeError": "Invalid data type",
        "ObjectIdError": "Invalid ID format",
        "ConnectionError": "Service temporarily unavailable",
        "TimeoutError": "Request timeout",
    }

    return safe_messages.get(error_type, "An error occurred. Please try again.")
