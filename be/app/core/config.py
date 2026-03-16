"""Application Configuration"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import json


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "BotBot"
    DEBUG: bool = True
    SECRET_KEY: str
    API_PREFIX: str = "/api"

    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "botbot"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

    # SMS Service (Aliyun)
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = ""
    ALIYUN_SMS_TEMPLATE_CODE: str = ""

    # Claude API
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # CORS - 支持多种格式 (str or list)
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Payment Settings
    RECHARGE_EXCHANGE_RATE: float = 10.0
    WITHDRAWAL_EXCHANGE_RATE: float = 10.0
    PLATFORM_FEE_RATE: float = 0.10
    MIN_RECHARGE_AMOUNT: float = 1.0
    MIN_WITHDRAWAL_AMOUNT: float = 100.0

    # Admin Configuration
    SUPER_ADMIN_PHONE: str = ""
    MIN_PLATFORM_WITHDRAWAL_AMOUNT: float = 1000.0

    # Task Settings
    MAX_BIDS_PER_TASK: int = 10
    TASK_CANCELLATION_PENALTY_RATE: float = 0.03  # 3% per bidder
    SELECTION_PHASE_DEADLINE_HOURS: int = 72      # 3 days

    # Arbitration Settings
    ARBITRATION_RESPONSE_DEADLINE_HOURS: int = 168  # 7 days

    # Alipay
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY_PATH: str = ""
    ALIPAY_PUBLIC_KEY_PATH: str = ""
    ALIPAY_NOTIFY_URL: str = ""
    ALIPAY_RETURN_URL: str = ""
    ALIPAY_GATEWAY: str = "https://openapi.alipay.com/gateway.do"

    # WeChat Pay
    WECHAT_APP_ID: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_APICLIENT_CERT_PATH: str = ""
    WECHAT_APICLIENT_KEY_PATH: str = ""
    WECHAT_NOTIFY_URL: str = ""

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from various formats"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            # Try JSON format
            if v.startswith('['):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Return as-is, will be parsed in get_cors_origins()
            return v
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        """
        Get CORS origins as a list

        Supports multiple formats:
        1. JSON array: ["http://localhost:3000","http://example.com"]
        2. Comma-separated: http://localhost:3000,http://example.com
        3. Single string: http://localhost:3000
        """
        if not self.CORS_ORIGINS:
            return ["http://localhost:3000"]

        # Already parsed as list by validator
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS

        # Parse string format
        origins_str = str(self.CORS_ORIGINS).strip()

        # Try comma-separated
        if ',' in origins_str:
            return [origin.strip() for origin in origins_str.split(',') if origin.strip()]

        # Single origin
        return [origins_str]


settings = Settings()
