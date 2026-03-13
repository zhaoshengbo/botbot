"""SMS Service for sending verification codes"""
import random
import string
from typing import Optional
from app.core.config import settings

# For development, we'll use a simple mock SMS service
# In production, replace with actual Aliyun SMS API calls


class SMSService:
    """SMS service for sending verification codes"""

    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Generate random verification code"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    async def send_verification_code(phone_number: str, code: str) -> bool:
        """
        Send verification code via SMS

        Args:
            phone_number: Phone number to send to
            code: Verification code

        Returns:
            True if sent successfully, False otherwise
        """
        # For development: just print the code
        if settings.DEBUG:
            print(f"[SMS Mock] Sending code {code} to {phone_number}")
            return True

        # TODO: Implement actual Aliyun SMS API call
        # from aliyunsdkcore.client import AcsClient
        # from aliyunsdkcore.request import CommonRequest
        #
        # client = AcsClient(
        #     settings.ALIYUN_ACCESS_KEY_ID,
        #     settings.ALIYUN_ACCESS_KEY_SECRET,
        #     'default'
        # )
        #
        # request = CommonRequest()
        # request.set_accept_format('json')
        # request.set_domain('dysmsapi.aliyuncs.com')
        # request.set_method('POST')
        # request.set_protocol_type('https')
        # request.set_version('2017-05-25')
        # request.set_action_name('SendSms')
        #
        # request.add_query_param('PhoneNumbers', phone_number)
        # request.add_query_param('SignName', settings.ALIYUN_SMS_SIGN_NAME)
        # request.add_query_param('TemplateCode', settings.ALIYUN_SMS_TEMPLATE_CODE)
        # request.add_query_param('TemplateParam', f'{{"code":"{code}"}}')
        #
        # response = client.do_action_with_exception(request)
        # return True

        return True


sms_service = SMSService()
