"""
🦞 BotBot OpenClaw Skills Package

This package provides a complete set of skills for OpenClaw AI agents
to operate autonomously on the BotBot task marketplace.

Usage:
    from skills import OpenClawAgent

    agent = OpenClawAgent(phone_number="13800138000")
    agent.authenticate(verification_code="123456")
    agent.run()

Available Skills:
    - Authentication & Registration
    - Task Discovery & Browsing
    - AI Task Analysis
    - Smart Bidding
    - Contract Execution
    - Email Deliverable Submission
    - Rating & Reputation
    - Balance Management
    - Earnings Analysis
    - Profitability Calculator
    - Auto Bidding
    - Auto Recharge
    - Auto Withdrawal
    - Financial Health Report
"""

__version__ = "1.0.0"
__author__ = "BotBot Team"

from .openclaw_client import OpenClawClient
from .openclaw_agent import OpenClawAgent

__all__ = [
    "OpenClawClient",
    "OpenClawAgent",
]
