"""
CA3003BOT - Crypto Analyzer Telegram Bot Package
"""

__version__ = "1.0.0"
__author__ = "SamSite101"
__description__ = "Crypto Analyzer Telegram Bot"

# Package imports
from .user_database import UserDatabase
from .payment_handler import PaymentHandler
from .crypto_scalping_bot import CryptoScalpingBot
from .claude_api import ClaudeAPI
from .binance_api_client import BinanceAPIClient

__all__ = [
    "UserDatabase",
    "PaymentHandler", 
    "CryptoScalpingBot",
    "ClaudeAPI",
    "BinanceAPIClient"
]