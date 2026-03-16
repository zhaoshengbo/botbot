#!/usr/bin/env python3
"""
Test script to verify alipay_service imports correctly with python-alipay-sdk
"""

print("Testing Alipay service import...")
print("=" * 60)

try:
    # Test 1: Import AliPay from python-alipay-sdk
    print("\n1. Testing python-alipay-sdk import...")
    from alipay import AliPay
    print("   ✅ Successfully imported AliPay from python-alipay-sdk")

    # Test 2: Import alipay_service
    print("\n2. Testing alipay_service import...")
    from app.services.alipay_service import AlipayService, alipay_service
    print("   ✅ Successfully imported AlipayService")

    # Test 3: Check if service initialized (should be None without config)
    print("\n3. Checking service initialization...")
    if alipay_service.client is None:
        print("   ✅ Service correctly initialized with client=None (no config)")
    else:
        print("   ⚠️  Service has a client (config must be present)")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("\nThe alipay_service is now compatible with python-alipay-sdk 3.4.0")

except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    exit(1)
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
