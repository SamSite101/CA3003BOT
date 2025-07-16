import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode
from user_database import UserDatabase
from payment_handler import PaymentHandler
from claude_api import ClaudeAPI

class CryptoScalpingBot:
    """Hauptlogik des Crypto Scalping Bots."""
    
    def __init__(self, telegram_token: str, anthropic_api_key: str, payment_token: str):
        """Initialisiert den Bot und seine Komponenten."""
        self.db = UserDatabase()
        self.payment_handler = PaymentHandler(payment_token)
        self.claude_api = ClaudeAPI(anthropic_api_key)
        self.telegram_token = telegram_token

    async def start(self, update: Update, context) -> None:
        """Begrüßt den Nutzer und zeigt die verfügbaren Befehle."""
        user_id = update.effective_user.id
        await self.db.get_user_data(user_id)
        
        welcome_text = """
🚀 **Willkommen beim Crypto Scalping Bot!**

Ich bin dein AI-Assistent für Crypto-Trading mit Claude Haiku 3.5 Power!

**Verfügbare Befehle:**
• `/analyze [COIN]` - Marktanalyse
• `/scalp [COIN]` - Scalping-Signale
• `/pricing` - Abonnement-Optionen
• `/status` - Dein Account-Status
• `/help` - Hilfe
        """
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

    async def analyze(self, update: Update, context) -> None:
        """Analysiert den Markt und gibt eine Antwort zurück."""
        user_id = update.effective_user.id
        user_data = await self.db.get_user_data(user_id)
        
        can_request, error_msg = self.can_make_request(user_data)
        if not can_request:
            await update.message.reply_text(error_msg)
            return
        
        coin = context.args[0].upper() if context.args else None
        if not coin:
            await update.message.reply_text("Bitte gib eine Coin an: `/analyze BTC`", parse_mode=ParseMode.MARKDOWN)
            return
        
        loading_msg = await update.message.reply_text(f"🔍 Analysiere {coin}... (powered by Claude Haiku 3.5)")
        
        prompt = f"Analysiere die aktuelle Marktlage von {coin}. Gib mir eine präzise Scalping-Einschätzung mit Einstiegspunkten, Stop-Loss und Take-Profit Levels."
        response = await self.claude_api.query(prompt)
        
        await self.db.update_user_requests(user_id)
        
        analysis_text = f"""
📊 **{coin} Scalping-Analyse**

{response}

⚡ *Powered by Claude Haiku 3.5*
        """
        
        await loading_msg.edit_text(analysis_text, parse_mode=ParseMode.MARKDOWN)

    def can_make_request(self, user_data) -> tuple:
        """Überprüft, ob der Nutzer eine Anfrage stellen kann."""
        if user_data[2] == 'free' and user_data[4] >= 10:
            return False, "Tägliches Limit erreicht."
        return True, ""
