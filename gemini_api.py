import requests

class GeminiAPI:
    def __init__(self):
        self.base_url = "https://api.gemini.com/v1"
        self.session = requests.Session()
    
    def get_ticker(self, pair):
        try:
            url = f"{self.base_url}/pubticker/{pair}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            return {"pair": pair, "price": float(data.get("last", 0))}
        except:
            return None

gemini = GeminiAPI()