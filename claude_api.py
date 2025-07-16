import anthropic

class ClaudeAPI:
    """Verwaltet die Kommunikation mit der Claude-API."""
    
    def __init__(self, api_key: str):
        """Initialisiert die Verbindung zur Claude-API."""
        self.client = anthropic.Anthropic(api_key=api_key)

    async def query(self, prompt: str) -> str:
        """
        Sendet eine Anfrage an die Claude-API.
        
        :param prompt: Die Anfrage, die an die API gesendet werden soll
        :return: Die Antwort der API
        """
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Fehler bei der Analyse: {str(e)}"
