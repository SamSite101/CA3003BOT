from binance.client import Client
import os
import asyncio


class BinanceAPIClient:
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialisiert den BinanceAPIClient mit den API-Schlüsseln.
        Args:
            api_key (str): Ihr Binance API-Schlüssel.
            api_secret (str): Ihr Binance API-Geheimnis.
        """
        if not api_key or not api_secret:
            raise ValueError("Binance API Key oder Secret ist nicht gesetzt. Bitte prüfen Sie Ihre .env-Datei.")
        self.client = Client(api_key, api_secret)

    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> list:
        """
        Ruft Candlestick-Daten (Klines) von Binance ab.

        Args:
            symbol (str): Das Handelspaar (z.B. 'BTCUSDT', 'ETHUSDT').
            interval (str): Das Zeitintervall (z.B. '1m', '5m', '1h', '1d').
            limit (int): Die maximale Anzahl der zurückzugebenden Candlesticks (max. 1000).

        Returns:
            list: Eine Liste von Listen, wobei jede innere Liste einen Candlestick darstellt.
                  Format: [Open time, Open, High, Low, Close, Volume, Close time,
                           Quote asset volume, Number of trades, Taker buy base asset volume,
                           Taker buy quote asset volume, Ignore]
        """
        try:
            # Die Binance-Client-Methoden sind synchron.
            # Wir müssen sie in einem Thread-Pool ausführen, um sie nicht zu blockieren,
            # wenn wir sie in einer asynchronen Umgebung (wie dem Telegram Bot) nutzen.
            # asyncio.to_thread ist hierfür ideal.
            klines = await asyncio.to_thread(
                self.client.get_klines, symbol=symbol, interval=interval, limit=limit
            )
            return klines
        except Exception as e:
            print(f"Fehler beim Abrufen der Klines für {symbol} ({interval}): {e}")
            return []

    async def get_current_price(self, symbol: str) -> float | None:
        """
        Ruft den aktuellen Preis eines Handelspaares ab.

        Args:
            symbol (str): Das Handelspaar (z.B. 'BTCUSDT').

        Returns:
            float | None: Der aktuelle Preis als Float oder None bei Fehler.
        """
        try:
            ticker = await asyncio.to_thread(
                self.client.get_symbol_ticker, symbol=symbol
            )
            return float(ticker['price'])
        except Exception as e:
            print(f"Fehler beim Abrufen des aktuellen Preises für {symbol}: {e}")
            return None


# Beispiel für die Verwendung (nur zum Testen)
async def main():
    from dotenv import load_dotenv
    load_dotenv()

    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_API_SECRET")

    if not binance_api_key or not binance_api_secret:
        print("Binance API Key oder Secret nicht gefunden. Bitte setzen Sie sie in Ihrer .env-Datei.")
        return

    binance_client = BinanceAPIClient(binance_api_key, binance_api_secret)

    # Beispiel: Letzte 100 1-Stunden-Candlesticks für BTC/USDT abrufen
    print("Rufe letzte 100 1-Stunden-Candlesticks für BTCUSDT ab...")
    klines_data = await binance_client.get_klines(symbol='BTCUSDT', interval='1h', limit=100)
    if klines_data:
        print(f"Erfolgreich {len(klines_data)} Candlesticks abgerufen.")
        # Beispiel: Den Schlusskurs des letzten Candlesticks ausgeben
        print(f"Letzter Schlusskurs: {klines_data[-1][4]}")
    else:
        print("Keine Candlesticks abgerufen.")

    # Beispiel: Aktuellen Preis von ETH/USDT abrufen
    print("\nRufe aktuellen Preis für ETHUSDT ab...")
    current_eth_price = await binance_client.get_current_price(symbol='ETHUSDT')
    if current_eth_price:
        print(f"Aktueller ETHUSDT Preis: {current_eth_price}")
    else:
        print("Aktueller ETHUSDT Preis konnte nicht abgerufen werden.")


if __name__ == "__main__":
    asyncio.run(main())
