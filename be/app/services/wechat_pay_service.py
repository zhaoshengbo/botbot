"""WeChat Pay Service"""
from typing import Dict, Any, Optional
from wechatpy.pay import WeChatPay
from wechatpy.exceptions import WeChatPayException
import xml.etree.ElementTree as ET

from app.core.config import settings


class WechatPayService:
    """WeChat Pay integration service"""

    def __init__(self):
        """Initialize WeChat Pay SDK"""
        # Skip initialization if no config (for development)
        if not settings.WECHAT_APP_ID or not settings.WECHAT_MCH_ID:
            self.pay = None
            return

        try:
            self.pay = WeChatPay(
                appid=settings.WECHAT_APP_ID,
                api_key=settings.WECHAT_API_KEY,
                mch_id=settings.WECHAT_MCH_ID,
                mch_cert=settings.WECHAT_APICLIENT_CERT_PATH if settings.WECHAT_APICLIENT_CERT_PATH else None,
                mch_key=settings.WECHAT_APICLIENT_KEY_PATH if settings.WECHAT_APICLIENT_KEY_PATH else None
            )
        except Exception as e:
            print(f"Warning: WeChat Pay initialization failed: {e}")
            self.pay = None

    async def create_order(
        self,
        order_no: str,
        amount: float,
        description: str,
        client_ip: str = "127.0.0.1",
        trade_type: str = "NATIVE"
    ) -> Dict[str, Any]:
        """
        Create unified order

        Args:
            order_no: Order number
            amount: Amount in RMB (will be converted to fen)
            description: Order description
            client_ip: Client IP address
            trade_type: NATIVE (QR code), JSAPI (in-app), MWEB (H5)

        Returns:
            Payment info dict
        """
        if not self.pay:
            raise RuntimeError("WeChat Pay not configured")

        # Convert RMB to fen (分)
        total_fee = int(amount * 100)

        try:
            # Create order
            result = self.pay.order.create(
                trade_type=trade_type,
                body=description,
                out_trade_no=order_no,
                total_fee=total_fee,
                notify_url=settings.WECHAT_NOTIFY_URL,
                spbill_create_ip=client_ip
            )

            # Return payment info based on trade type
            if trade_type == "NATIVE":
                # QR code payment
                return {
                    "code_url": result.get("code_url"),
                    "prepay_id": result.get("prepay_id")
                }
            elif trade_type == "JSAPI":
                # In-app payment
                return {
                    "appid": result.get("appid"),
                    "prepay_id": result.get("prepay_id"),
                    "timestamp": result.get("timestamp"),
                    "nonce_str": result.get("nonce_str"),
                    "sign": result.get("sign")
                }
            elif trade_type == "MWEB":
                # H5 payment
                return {
                    "mweb_url": result.get("mweb_url"),
                    "prepay_id": result.get("prepay_id")
                }
            else:
                return result

        except WeChatPayException as e:
            print(f"WeChat Pay order creation failed: {e}")
            raise RuntimeError(f"WeChat Pay error: {e.errmsg}")

    async def verify_notify(self, xml_data: str) -> Optional[Dict[str, Any]]:
        """
        Verify async notification

        Args:
            xml_data: XML notification data from WeChat

        Returns:
            Parsed notification dict if valid, None otherwise
        """
        if not self.pay:
            raise RuntimeError("WeChat Pay not configured")

        try:
            # Parse XML
            data = self.pay.parse_payment_result(xml_data)

            # Verify signature (done by parse_payment_result)
            # Check result code
            if data.get("return_code") == "SUCCESS" and data.get("result_code") == "SUCCESS":
                return {
                    "out_trade_no": data.get("out_trade_no"),
                    "transaction_id": data.get("transaction_id"),
                    "total_fee": int(data.get("total_fee", 0)) / 100.0,  # Convert fen to RMB
                    "time_end": data.get("time_end"),
                    "trade_state": "SUCCESS"
                }
            else:
                print(f"WeChat Pay notification failed: {data}")
                return None

        except Exception as e:
            print(f"WeChat Pay notification verification failed: {e}")
            return None

    async def query_order(self, order_no: str) -> Optional[Dict[str, Any]]:
        """
        Query order status

        Args:
            order_no: Order number

        Returns:
            Order info dict if found, None otherwise
        """
        if not self.pay:
            raise RuntimeError("WeChat Pay not configured")

        try:
            # Query order
            result = self.pay.order.query(out_trade_no=order_no)

            # Check result
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {
                    "out_trade_no": result.get("out_trade_no"),
                    "transaction_id": result.get("transaction_id"),
                    "trade_state": result.get("trade_state"),
                    "total_fee": int(result.get("total_fee", 0)) / 100.0,  # Convert fen to RMB
                    "time_end": result.get("time_end")
                }
            else:
                print(f"WeChat Pay query failed: {result}")
                return None

        except WeChatPayException as e:
            print(f"WeChat Pay query exception: {e}")
            return None

    @staticmethod
    def generate_success_xml() -> str:
        """
        Generate success response XML for WeChat callback
        """
        return """<xml>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <return_msg><![CDATA[OK]]></return_msg>
</xml>"""

    @staticmethod
    def generate_fail_xml(msg: str = "FAIL") -> str:
        """
        Generate fail response XML for WeChat callback
        """
        return f"""<xml>
  <return_code><![CDATA[FAIL]]></return_code>
  <return_msg><![CDATA[{msg}]]></return_msg>
</xml>"""


# Create singleton instance
wechat_pay_service = WechatPayService()
