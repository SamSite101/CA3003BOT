"""
Crypto Scalping Bot - Telegram Bot Implementation
"""

import datetime
import asyncio
import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from user_database import UserDatabase
from payment_handler import PaymentHandler

# Load environment variables
load_dotenv()


class CryptoScalpingBot:
    """Main Telegram bot class for crypto scalping functionality."""

    def __init__(self, token: str, anthropic_api_key: str, user_db: UserDatabase,
                 payment_handler_param: PaymentHandler):
        """
        Initialize the CryptoScalpingBot.

        Args:
            token (str): Telegram Bot Token
            anthropic_api_key (str): Anthropic API Key
            user_db (UserDatabase): UserDatabase instance
            payment_handler_param (PaymentHandler): PaymentHandler instance
        """
        self.application = Application.builder().token(token).build()
        self.anthropic_api_key = anthropic_api_key
        self.db = user_db
        self.payment_handler = payment_handler_param

        # Register command handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all command and callback handlers."""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(CommandHandler("check_subscription", self.check_subscription))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message and add user to database."""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        await self.db.add_user(user_id, username)

        await update.message.reply_text(
            f"Hallo {username}! Willkommen beim Crypto Scalping Bot. "
            "Ich helfe Ihnen, profitable Handelsmöglichkeiten zu finden."
        )

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Display subscription options."""
        keyboard = [
            [InlineKeyboardButton("Basic (30 Tage - $10)", callback_data="subscribe_basic")],
            [InlineKeyboardButton("Premium (90 Tage - $25)", callback_data="subscribe_premium")],
            [InlineKeyboardButton("VIP (365 Tage - $80)", callback_data="subscribe_vip")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Wählen Sie Ihr Abonnement:", reply_markup=reply_markup)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries from inline buttons."""
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()

        if query.data.startswith("subscribe_"):
            subscription_type = query.data.split("_")[1]
            price = await self.payment_handler.get_subscription_price(subscription_type)

            if price is not None:
                payment_successful = await self.payment_handler.handle_payment(user_id, subscription_type)
                if payment_successful:
                    await query.edit_message_text(
                        f"Vielen Dank! Ihr {subscription_type}-Abonnement wurde erfolgreich aktiviert."
                    )
                else:
                    await query.edit_message_text(
                        f"Die Aktivierung Ihres {subscription_type}-Abonnements ist fehlgeschlagen."
                    )
            else:
                await query.edit_message_text("Ungültiger Abonnementtyp ausgewählt.")

    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check user subscription status."""
        user_id = update.effective_user.id
        user_data = await self.db.get_user(user_id)

        if user_data and user_data.get('subscription_type'):
            subscription_type = user_data['subscription_type']
            end_date = user_data.get('subscription_end_date', 'Unbekannt')
            await update.message.reply_text(
                f"Ihr aktuelles Abonnement: {subscription_type}\n"
                f"Gültig bis: {end_date}"
            )
        else:
            await update.message.reply_text("Sie haben derzeit kein aktives Abonnement.")

    @staticmethod
    async def can_make_request(user_id: int) -> bool:
        """Check if user can make requests based on subscription status."""
        # Placeholder - implement actual subscription check
        return True

    async def run(self):
        """Start the bot."""
        print("Bot wird gestartet...")
        await self.db.connect()

        try:
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        finally:
            await self.db.close()


# Only run if called directly (not imported)
if __name__ == "__main__":
    print("Warning: Running bot directly from crypto_scalping_bot.py")
    print("Consider using main.py instead for proper project structure.")

    # Get environment variables
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    if not TOKEN or not ANTHROPIC_API_KEY:
        print("ERROR: Missing environment variables!")
        exit(1)

    # Initialize components
    db_instance = UserDatabase()
    payment_handler_instance = PaymentHandler(db_instance)

    # Create and run bot
    bot = CryptoScalpingBot(
        TOKEN, ANTHROPIC_API_KEY,
        db_instance, payment_handler_instance
    )

    asyncio.run(bot.run())