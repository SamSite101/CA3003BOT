from telegram import LabeledPrice
from datetime import datetime, timedelta

class PaymentHandler:
    """Verwaltet alle Zahlungen und Abonnement-Updates."""
    
    def __init__(self, payment_provider_token: str):
        """Initialisiert den Zahlungsanbieter."""
        self.payment_provider_token = payment_provider_token

    async def create_invoice(self, chat_id: int, plan: str, price: int, context) -> None:
        """
        Erstellt eine Zahlungsrechnung.
        
        :param chat_id: ID des Chats
        :param plan: Abonnementplan
        :param price: Preis des Abonnements
        :param context: Telegram Bot Kontext
        """
        await context.bot.send_invoice(
            chat_id=chat_id,
            title=f"Crypto Scalping Bot - {plan.upper()}",
            description=f"{plan.upper()} Abonnement für 1 Monat",
            payload=f"subscription_{plan}",
            provider_token=self.payment_provider_token,
            currency="USD",
            prices=[LabeledPrice(f"{plan.upper()} Abonnement", price)]
        )

    async def handle_payment(self, user_id: int, plan: str, db: UserDatabase):
        """
        Bearbeitet die erfolgreiche Zahlung und aktualisiert das Abonnement.
        
        :param user_id: ID des Nutzers
        :param plan: Abonnementplan
        :param db: Instanz der UserDatabase
        """
        expires = datetime.now() + timedelta(days=30)
        await db.update_user_subscription(user_id, plan, expires)

    async def validate_payment(self, payment_amount: int, plan: str) -> bool:
        """
        Validiert die Zahlung.
        
        :param payment_amount: Der bezahlte Betrag
        :param plan: Der gewählte Plan
        :return: True, wenn die Zahlung gültig ist
        """
        price = PRICES.get(plan)
        if price and payment_amount == price:
            return True
        return False
