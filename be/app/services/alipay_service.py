"""Alipay Payment Service"""
import os
from typing import Dict, Any, Optional
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeWapPayModel import AlipayTradeWapPayModel
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeWapPayRequest import AlipayTradeWapPayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.util.SignatureUtils import verify_with_rsa

from app.core.config import settings


class AlipayService:
    """Alipay payment integration service"""

    def __init__(self):
        """Initialize Alipay SDK"""
        # Skip initialization if no config (for development)
        if not settings.ALIPAY_APP_ID:
            self.client = None
            return

        # Initialize config
        self.config = AlipayClientConfig()
        self.config.server_url = settings.ALIPAY_GATEWAY
        self.config.app_id = settings.ALIPAY_APP_ID

        # Read private key
        if settings.ALIPAY_PRIVATE_KEY_PATH and os.path.exists(settings.ALIPAY_PRIVATE_KEY_PATH):
            with open(settings.ALIPAY_PRIVATE_KEY_PATH, 'r') as f:
                self.config.app_private_key = f.read()
        else:
            print("Warning: Alipay private key not found")
            self.client = None
            return

        # Read public key
        if settings.ALIPAY_PUBLIC_KEY_PATH and os.path.exists(settings.ALIPAY_PUBLIC_KEY_PATH):
            with open(settings.ALIPAY_PUBLIC_KEY_PATH, 'r') as f:
                self.config.alipay_public_key = f.read()
        else:
            print("Warning: Alipay public key not found")
            self.client = None
            return

        # Create client
        self.client = DefaultAlipayClient(alipay_client_config=self.config)

    async def create_page_pay(
        self,
        order_no: str,
        amount: float,
        subject: str,
        return_url: Optional[str] = None
    ) -> str:
        """
        Create PC web payment
        Returns: Payment form HTML
        """
        if not self.client:
            raise RuntimeError("Alipay not configured")

        # Create payment model
        model = AlipayTradePagePayModel()
        model.out_trade_no = order_no
        model.total_amount = f"{amount:.2f}"
        model.subject = subject
        model.product_code = "FAST_INSTANT_TRADE_PAY"

        # Create request
        request = AlipayTradePagePayRequest(biz_model=model)
        request.notify_url = settings.ALIPAY_NOTIFY_URL
        request.return_url = return_url or settings.ALIPAY_RETURN_URL

        # Execute request
        response = self.client.page_execute(request, http_method="GET")
        return response

    async def create_wap_pay(
        self,
        order_no: str,
        amount: float,
        subject: str,
        return_url: Optional[str] = None
    ) -> str:
        """
        Create mobile WAP payment
        Returns: Payment form HTML
        """
        if not self.client:
            raise RuntimeError("Alipay not configured")

        # Create payment model
        model = AlipayTradeWapPayModel()
        model.out_trade_no = order_no
        model.total_amount = f"{amount:.2f}"
        model.subject = subject
        model.product_code = "QUICK_WAP_WAY"

        # Create request
        request = AlipayTradeWapPayRequest(biz_model=model)
        request.notify_url = settings.ALIPAY_NOTIFY_URL
        request.return_url = return_url or settings.ALIPAY_RETURN_URL

        # Execute request
        response = self.client.page_execute(request, http_method="GET")
        return response

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

        # Remove sign and sign_type from params
        verify_params = {k: v for k, v in params.items() if k not in ["sign", "sign_type"]}

        # Sort parameters
        sorted_params = sorted(verify_params.items())
        message = "&".join([f"{k}={v}" for k, v in sorted_params])

        # Verify signature
        try:
            return verify_with_rsa(
                self.config.alipay_public_key.encode('utf-8'),
                message.encode('utf-8'),
                sign
            )
        except Exception as e:
            print(f"Alipay signature verification failed: {e}")
            return False

    async def query_order(self, order_no: str) -> Optional[Dict[str, Any]]:
        """
        Query order status
        """
        if not self.client:
            raise RuntimeError("Alipay not configured")

        # Create query model
        model = AlipayTradeQueryModel()
        model.out_trade_no = order_no

        # Create request
        request = AlipayTradeQueryRequest(biz_model=model)

        try:
            # Execute request
            response = self.client.execute(request)

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
