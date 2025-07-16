import datetime

# Annahme: Die UserDatabase-Klasse ist in user_database.py definiert.
# Dieser Import ist entscheidend, um den Fehler "Unresolved reference 'UserDatabase'" zu beheben.
from user_database import UserDatabase

# Definition der Preise direkt in dieser Datei für die Demo.
# In einer realen Anwendung würden Sie dies wahrscheinlich aus einer zentralen Konfigurationsdatei importieren
# (z.B. from config import PRICES), um die Wartung zu erleichtern.
PRICES = {
    "basic": {"duration_days": 30, "price_usd": 10.00},
    "premium": {"duration_days": 90, "price_usd": 25.00},
    "vip": {"duration_days": 365, "price_usd": 80.00},
}


class PaymentHandler:
    def __init__(self, db: UserDatabase):
        """
        Initialisiert den PaymentHandler mit einer Instanz der UserDatabase.
        Args:
            db (UserDatabase): Eine Instanz der UserDatabase zur Interaktion mit der Datenbank.
        """
        self.db = db

    async def handle_payment(self, user_id: int, subscription_type: str) -> bool:
        """
        Verarbeitet den Zahlungsvorgang für das Abonnement eines Benutzers.
        Aktualisiert das Abonnement des Benutzers in der Datenbank.

        Diese Methode verwendet 'self.db' und sollte daher eine Instanzmethode sein (nicht statisch).

        Args:
            user_id (int): Die ID des Benutzers.
            subscription_type (str): Der Typ des Abonnements (z.B. "basic", "premium", "vip").

        Returns:
            bool: True, wenn die Zahlung erfolgreich war und das Abonnement aktualisiert wurde,
                  andernfalls False.
        """
        if subscription_type not in PRICES:
            print(f"Fehler: Ungültiger Abonnementtyp '{subscription_type}'")
            return False

        # Hier würde in einem realen Szenario die Integration mit einem Zahlungs-Gateway erfolgen.
        # Für den Moment simulieren wir einen erfolgreichen Zahlungsvorgang.
        payment_successful = True  # Simulation des Zahlungserfolgs

        if payment_successful:
            duration_days = PRICES[subscription_type]["duration_days"]
            current_date = datetime.date.today()

            # Aktuelles Abonnement-Enddatum des Benutzers abrufen
            user_data = await self.db.get_user(user_id)

            if user_data and user_data.get('subscription_end_date'):
                # Wenn der Benutzer bereits ein Abonnement hat, verlängern Sie es ab dem aktuellen Enddatum
                # Sicherstellen, dass das Datum korrekt geparst wird, falls es None oder leer ist
                try:
                    current_end_date_str = user_data['subscription_end_date']
                    if current_end_date_str:
                        current_end_date = datetime.datetime.strptime(current_end_date_str, '%Y-%m-%d').date()
                        # Wenn das aktuelle Enddatum in der Vergangenheit liegt, starten Sie das neue Abonnement ab heute
                        if current_end_date < current_date:
                            new_end_date = current_date + datetime.timedelta(days=duration_days)
                        else:
                            new_end_date = current_end_date + datetime.timedelta(days=duration_days)
                    else:
                        # Wenn das Enddatum leer ist, starten Sie ab heute
                        new_end_date = current_date + datetime.timedelta(days=duration_days)
                except (ValueError, TypeError):
                    # Bei Fehlern beim Parsen des Datums, starten Sie ab heute
                    new_end_date = current_date + datetime.timedelta(days=duration_days)
            else:
                # Wenn kein bestehendes Abonnement vorhanden ist, starten Sie ab heute
                new_end_date = current_date + datetime.timedelta(days=duration_days)

            await self.db.update_user_subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                subscription_end_date=new_end_date.strftime('%Y-%m-%d')
            )
            print(f"Benutzer {user_id} hat {subscription_type} abonniert bis {new_end_date}")
            return True
        else:
            print(f"Zahlung für Benutzer {user_id} für {subscription_type} fehlgeschlagen")
            return False

    @staticmethod
    def validate_payment(amount_paid: float, expected_amount: float) -> bool:
        """
        Überprüft, ob der gezahlte Betrag dem erwarteten Betrag entspricht.
        Da diese Methode keine Instanzattribute (self) verwendet, ist sie als statische Methode markiert.

        Args:
            amount_paid (float): Der tatsächlich gezahlte Betrag.
            expected_amount (float): Der erwartete Betrag für das Abonnement.

        Returns:
            bool: True, wenn der gezahlte Betrag ausreicht, andernfalls False.
        """
        return amount_paid >= expected_amount

    async def get_subscription_price(self, subscription_type: str) -> float | None:
        """
        Gibt den Preis eines bestimmten Abonnementtyps zurück.

        Args:
            subscription_type (str): Der Typ des Abonnements.

        Returns:
            float | None: Der Preis des Abonnements in USD oder None, wenn der Typ ungültig ist.
        """
        return PRICES.get(subscription_type, {}).get("price_usd")

