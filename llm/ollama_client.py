import requests
from llm.prompt_builder import build_system_prompt

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL  = "mistral"

SYSTEM_PROMPT = build_system_prompt()


def ask_mistral(conversation: list) -> str:
    """
    Envoie la conversation complète à Mistral via Ollama.

    conversation = liste de messages :
    [
      {"role": "user",      "content": "bonjour j ai mal a une dent"},
      {"role": "assistant", "content": "Je comprends..."},
      {"role": "user",      "content": "depuis hier soir"},
    ]
    """
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model"   : OLLAMA_MODEL,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + conversation,
                "stream"  : False,
                "options" : {
                    "temperature": 0.3,
                    "num_predict": 150,
                }
            },
            timeout=120
        )
        return r.json()['message']['content']

    except requests.exceptions.ConnectionError:
        print("? Ollama non démarré  lancer : ollama serve")
        return "Je suis désolé, une erreur technique est survenue. Veuillez patienter."

    except requests.exceptions.Timeout:
        print("? Timeout Ollama  augmenter timeout ou vérifier le modèle")
        return "Je suis désolé, je mets un peu de temps à répondre. Pouvez-vous répéter ?"

    except Exception as e:
        print(f"? Erreur Mistral : {e}")
        return "Je suis désolé, une erreur technique est survenue."
