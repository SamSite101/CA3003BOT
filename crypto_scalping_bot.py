# Imports for the Telegram Bot
import datetime  # Necessary for date operations
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Imports for UserDatabase and PaymentHandler
from user_database import UserDatabase
from payment_handler import PaymentHandler

import asyncio
import os  # Necessary for os.getenv
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Load tokens from environment variables.
# Make sure these variables are defined in your .env file, e.g.:
# TELEGRAM_BOT_TOKEN="YOUR_ACTUAL_TELEGRAM_BOT_TOKEN_HERE"
# ANTHROPIC_API_KEY="YOUR_ACTUAL_ANTHROPIC_API_KEY_HERE"
TOKEN = os.getenv("7815968799:AAEET2gcuhJMaFCfEbuEH7zNDrlqtWe0ivE")
ANTHROPIC_API_KEY = os.getenv("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")


class CryptoScalpingBot:
    def __init__(self, token: str, anthropic_api_key: str, db_instance: UserDatabase,
                 payment_handler_instance: PaymentHandler):
        """
        Initializes the CryptoScalpingBot.
        Args:
            token (str): Telegram Bot Token.
            anthropic_api_key (str): Anthropic API Key.
            db_instance (UserDatabase): Instance of UserDatabase.
            payment_handler_instance (PaymentHandler): Instance of PaymentHandler.
        """
        self.application = Application.builder().token(token).build()
        self.anthropic_api_key = anthropic_api_key
        self.db = db_instance
        self.payment_handler = payment_handler_instance

        # PyCharm warnings "Shadows name 'db_instance' from outer scope" and
        # "Shadows name 'payment_handler_instance' from outer scope" are addressed
        # by directly assigning the passed instances to self.db and self.payment_handler.
        # This is standard practice for dependency injection and is clear.

        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(CommandHandler("check_subscription", self.check_subscription))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends a welcome message and adds the user to the database."""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        # Add user to the database
        await self.db.add_user(user_id, username)

        await update.message.reply_text(
            f"Hello {username}! Welcome to the Crypto Scalping Bot. "
            "I will help you find profitable trading opportunities."
        )
        # PyCharm warning "Parameter 'context' value is not used":
        # The 'context' parameter is passed by python-telegram-bot by default,
        # even if not all its functionalities are used in every method.
        # This warning can be ignored here, as the parameter can be useful for
        # future extensions or advanced functionality.

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Displays subscription options."""
        # PyCharm warning "Method 'subscribe' may be static":
        # This method CANNOT be static, as it uses 'update.message.reply_text',
        # which is an asynchronous operation and requires the 'update' parameter.
        keyboard = [
            [InlineKeyboardButton("Basic (30 days - $10)", callback_data="subscribe_basic")],
            [InlineKeyboardButton("Premium (90 days - $25)", callback_data="subscribe_premium")],
            [InlineKeyboardButton("VIP (365 days - $80)", callback_data="subscribe_vip")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose your subscription:", reply_markup=reply_markup)
        # PyCharm warning "Parameter 'context' value is not used":
        # See comment in the 'start' method.

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handles callback queries from inline buttons."""
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()  # Acknowledges the callback

        if query.data.startswith("subscribe_"):
            subscription_type = query.data.split("_")[1]
            price = await self.payment_handler.get_subscription_price(subscription_type)

            if price is not None:
                # Here, the actual payment processing would begin
                # For the demo, we simulate a successful payment
                payment_successful = await self.payment_handler.handle_payment(user_id, subscription_type)
                if payment_successful:
                    await query.edit_message_text(
                        f"Thank you! Your {subscription_type} subscription has been successfully activated."
                    )
                else:
                    await query.edit_message_text(
                        f"The activation of your {subscription_type} subscription failed. Please try again."
                    )
            else:
                await query.edit_message_text("Invalid subscription type selected.")
        # PyCharm warning "Parameter 'context' value is not used":
        # See comment in the 'start' method.

    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Checks the user's subscription status."""
        user_id = update.effective_user.id
        user_data = await self.db.get_user(user_id)

        if user_data and user_data.get('subscription_end_date'):
            end_date_str = user_data['subscription_end_date']
            try:
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date >= datetime.date.today():
                    await update.message.reply_text(
                        f"Your current subscription ({user_data.get('subscription_type', 'N/A')}) is valid until: {end_date.strftime('%d.%m.%Y')}"
                    )
                else:
                    await update.message.reply_text("Your subscription has expired. Please renew it.")
            except ValueError:
                await update.message.reply_text("Error retrieving your subscription date.")
        else:
            await update.message.reply_text("You currently have no active subscription.")
        # PyCharm warning "Parameter 'context' value is not used":
        # See comment in the 'start' method.

    @staticmethod
    async def can_make_request(user_id: int) -> bool:
        """
        Checks if a user is allowed to make a request (e.g., based on subscription status).
        This method is now static as it does not use any instance attributes.
        """
        # PyCharm warning "Parameter 'user_id' value is not used":
        # In the current placeholder logic, 'user_id' is indeed not used,
        # as the method always returns True. In a real implementation,
        # 'user_id' would be used to retrieve and check the subscription status
        # from the database, e.g., await db.get_user_subscription_status(user_id).
        return True  # Placeholder

    def run(self):
        """Starts the bot."""
        print("Bot is starting...")
        # Establish database connection before starting the bot
        asyncio.run(self.db.connect())
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        # Close database connection when the bot is stopped (optional, can also be done in a shutdown handler)
        # asyncio.run(self.db.close())


if __name__ == "__main__":
    # Create an instance of UserDatabase
    db_instance = UserDatabase()
    # Create an instance of PaymentHandler and pass the db_instance
    payment_handler_instance = PaymentHandler(db_instance)

    # Initialize the bot
    bot = CryptoScalpingBot(TOKEN, ANTHROPIC_API_KEY, db_instance, payment_handler_instance)

    # Start the bot
    bot.run()

