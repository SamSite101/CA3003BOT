from anthropic import Anthropic
from anthropic.types import MessageParam  # Importiert MessageParam für korrekte Typisierung
import os


class ClaudeAPI:
    def __init__(self, api_key: str):
        """
        Initialisiert die ClaudeAPI mit dem Anthropic API-Schlüssel.
        Args:
            api_key (str): Ihr Anthropic API-Schlüssel.
        """
        if not api_key:
            raise ValueError(
                "Anthropic API Key ist nicht gesetzt. Bitte setzen Sie die Umgebungsvariable 'ANTHROPIC_API_KEY'.")
        self.client = Anthropic(api_key=api_key)

    async def generate_response(self, user_message: str, model: str = "claude-3-5-sonnet-20241022",
                                max_tokens: int = 1024) -> str:
        """
        Generiert eine Antwort mithilfe des Anthropic Claude Modells.

        Args:
            user_message (str): Die Nachricht des Benutzers.
            model (str): Das zu verwendende Claude-Modell.
            max_tokens (int): Die maximale Anzahl der Tokens in der Antwort.

        Returns:
            str: Die generierte Antwort des KI-Modells.
        """
        messages: list[MessageParam] = [
            {"role": "user", "content": user_message}
        ]

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages
            )
            # Überprüfen, ob die Antwort Textinhalt hat
            if response.content and response.content[0].text:
                return response.content[0].text
            else:
                return "Entschuldigung, ich konnte keine Textantwort generieren."
        except Exception as e:
            print(f"Fehler bei der Kommunikation mit der Anthropic API: {e}")
            return "Entschuldigung, bei der Kommunikation mit der KI ist ein Fehler aufgetreten."


# Beispiel für die Verwendung (nur zum Testen, kann in main.py oder crypto_scalping_bot.py integriert werden)
async def main():
    # Stellen Sie sicher, dass ANTHROPIC_API_KEY in Ihrer .env-Datei gesetzt ist
    from dotenv import load_dotenv
    load_dotenv()
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        print("ANTHROPIC_API_KEY nicht gefunden. Bitte setzen Sie ihn in Ihrer .env-Datei.")
        return

    claude_api = ClaudeAPI(api_key=anthropic_api_key)

    # Beispielnachricht
    response_text = await claude_api.generate_response("Was ist die Hauptstadt von Frankreich?")
    print(f"Claude antwortet: {response_text}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

