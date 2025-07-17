#!/usr/bin/env python3
"""
CA3003BOT - Crypto Analyzer Telegram Bot
Main entry point for the application.
"""

import os
import asyncio
from dotenv import load_dotenv

from user_database import UserDatabase
from payment_handler import PaymentHandler
from crypto_scalping_bot import CryptoScalpingBot


def main():
    """Main function to initialize and start the bot."""
    # Load environment variables
    load_dotenv()

    # Get tokens from environment
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not telegram_token or not anthropic_api_key:
        print("ERROR: Missing required environment variables!")
        print("Please check your .env file for:")
        print("- TELEGRAM_BOT_TOKEN")
        print("- ANTHROPIC_API_KEY")
        return

    # Initialize database and payment handler
    db_instance = UserDatabase()
    payment_handler_instance = PaymentHandler(db_instance)

    # Initialize and start bot
    bot = CryptoScalpingBot(
        token=telegram_token,
        anthropic_api_key=anthropic_api_key,
        user_db=db_instance,
        payment_handler_param=payment_handler_instance
    )

    print("Starting CA3003BOT...")
    bot.run()


if __name__ == "__main__":
    main()