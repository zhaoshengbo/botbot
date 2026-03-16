"""Alipay Payment Service"""
import os
from typing import Dict, Any, Optional
from alipay import AliPay

from app.core.config import settings


class AlipayService:
    """Alipay payment integration service"""

    def __init__(self):
        """Initialize Alipay SDK"""
        # Skip initialization if no config (for development)
        if not settings.ALIPAY_APP_ID:
            self.client = None
            return

        # Read private key
        app_private_key_string = None
        if settings.ALIPAY_PRIVATE_KEY_PATH and os.path.exists(settings.ALIPAY_PRIVATE_KEY_PATH):
            with open(settings.ALIPAY_PRIVATE_KEY_PATH, 'r') as f:
                app_private_key_string = f.read()
        else:
            print("Warning: Alipay private key not found")
            self.client = None
            return

        # Read public key
        alipay_public_key_string = None
        if settings.ALIPAY_PUBLIC_KEY_PATH and os.path.exists(settings.ALIPAY_PUBLIC_KEY_PATH):
            with open(settings.ALIPAY_PUBLIC_KEY_PATH, 'r') as f:
                alipay_public_key_string = f.read()
        else:
            print("Warning: Alipay public key not found")
            self.client = None
            return

        # Create client
        self.client = AliPay(
            appid=settings.ALIPAY_APP_ID,
            app_notify_url=settings.ALIPAY_NOTIFY_URL,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug="sandbox" in settings.ALIPAY_GATEWAY.lower()
        )

    async def create_page_pay(
        self,
        order_no: str,
        amount: float,
        subject: str,
        return_url: Optional[str] = None
    ) -> str:
        """
        Create PC web payment
        Returns: Payment URL
        """
        if not self.client:
            raise RuntimeError("Alipay not configured")

        # Build order string
        order_string = self.client.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=f"{amount:.2f}",
            subject=subject,
            return_url=return_url or settings.ALIPAY_RETURN_URL,
            notify_url=settings.ALIPAY_NOTIFY_URL
        )

        # Return full payment URL
        return f"{settings.ALIPAY_GATEWAY}?{order_string}"

    async def create_wap_pay(
        self,
        order_no: str,
        amount: float,
        subject: str,
        return_url: Optional[str] = None
    ) -> str:
        """
        Create mobile WAP payment
        Returns: Payment URL
        """
        if not self.client:
            raise RuntimeError("Alipay not configured")

        # Build order string
        order_string = self.client.api_alipay_trade_wap_pay(
            out_trade_no=order_no,
            total_amount=f"{amount:.2f}",
            subject=subject,
            return_url=return_url or settings.ALIPAY_RETURN_URL,
            notify_url=settings.ALIPAY_NOTIFY_URL
        )

        # Return full payment URL
        return f"{settings.ALIPAY_GATEWAY}?{order_string}"

    async def verify_notify(self, params: Dict[str, Any]) -> bool:
        """
        Verify async notification signature
        """
        if not self.client:
            raise RuntimeError("Alipay not configured")

        # Extract signature
        sign = params.get("sign")
        if not sign:
            return False

        # Verify signature using SDK
        try:
            return self.client.verify(params, sign)
        except Exception as e:
            print(f"Alipay signature verification failed: {e}")
            return False

    async def query_order(self, order_no: str) -> Optional[Dict[str, Any]]:
        """
        Query order status
        """
        if not self.client:
            raise RuntimeError("Alipay not configured")

        try:
            # Execute query
            response = self.client.api_alipay_trade_query(
                out_trade_no=order_no
            )

            # Parse response
            if response.get("code") == "10000":
                return {
                    "trade_no": response.get("trade_no"),
                    "out_trade_no": response.get("out_trade_no"),
                    "trade_status": response.get("trade_status"),
                    "total_amount": response.get("total_amount"),
                    "receipt_amount": response.get("receipt_amount")
                }
            else:
                print(f"Alipay query failed: {response}")
                return None
        except Exception as e:
            print(f"Alipay query exception: {e}")
            return None


# Create singleton instance
alipay_service = AlipayService()
