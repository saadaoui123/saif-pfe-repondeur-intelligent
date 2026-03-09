# saif-pfe-repondeur-intelligent

Répondeur Téléphonique Intelligent — Cabinet Dentaire de Groupe
Pipeline : STT (Vosk) → LLM (Mistral 7B) → TTS (edge-tts)

##  Table des matières
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage](#démarrage)
- [Tests](#tests)
- [Architecture](#architecture)
- [Dépannage](#dépannage)

---

## 1. Prérequis

- Ubuntu 22.04 / 24.04
- Python 3.8+
- 8 Go RAM minimum (16 Go recommandé)
- 10 Go d'espace disque
```bash
python3 --version
sudo apt update
sudo apt install -y curl git unzip net-tools
```

---

##  2. Installation

### 2.1 Cloner le dépôt
```bash
git clone https://github.com/saadaoui123/saif-pfe-repondeur-intelligent.git
cd saif-pfe-repondeur-intelligent
# OU
cd ~/saif_pfe
```

### 2.2 Environnement virtuel
```bash
python3 -m venv stt_env
source stt_env/bin/activate
which python
# Doit afficher : /home/saif/saif_pfe/stt_env/bin/python
```

### 2.3 Dépendances Python
```bash
pip install --upgrade pip
pip install vosk websockets requests numpy pytest
```

### 2.4 Ollama et Mistral 7B
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
ollama pull mistral
ollama list
# Doit afficher : mistral:latest
```

### 2.5 Zoiper5
Télécharger : https://www.zoiper.com/en/voip-softphone/download/current

Configuration SIP :
- **Domain** : `1001@<IP_de_votre_machine>`
- **Port** : `5060`
- **Utilisateur** : `1001`
- **Mot de passe** : `1234`
- **Numéro à appeler** : `700`

### 2.6 Modèles Vosk
```bash
ls -la models/
# vosk-model-fr-0.22.zip         → production (large — 1.4 GB)
# vosk-model-small-fr-0.22.zip   → test rapide

unzip models/vosk-model-small-fr-0.22.zip -d models/
```
> **Note** : modèle final utilisé en production → `vosk-model-fr-0.22` (large)

---

##  3. Configuration

### 3.1 Variables d'environnement
```bash
echo 'export OLLAMA_HOST="http://localhost:11434"' >> ~/.bashrc
echo 'export OLLAMA_MODEL="mistral"' >> ~/.bashrc
echo 'export VOSK_MODEL_PATH="models/vosk-model-small-fr-0.22"' >> ~/.bashrc
echo 'export SIP_PORT="5060"' >> ~/.bashrc
source ~/.bashrc
```

### 3.2 config.py
```python
OLLAMA_CONFIG = {
    "host": "http://localhost:11434",
    "model": "mistral",
    "temperature": 0.3
}
VOSK_CONFIG = {
    "model_path": "models/vosk-model-small-fr-0.22",
    "sample_rate": 8000
}
SIP_CONFIG = {
    "port": 5060,
    "domain": "localhost"
}
```

---

##  4. Démarrage

Ouvrir **3 terminaux** et exécuter dans l'ordre :

**Terminal 1 — Démarrer Ollama**
```bash
ollama serve
# Vérification :
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Bonjour, comment puis-je vous aider ?"
}'
```

**Terminal 2 — Serveur AudioSocket (Vosk)**
```bash
cd ~/saif_pfe
source ~/stt_env/bin/activate
python stt/audiosocket_vosk_server.py
# Le serveur écoute sur le port 6000
```

**Terminal 3 — Application principale**
```bash
cd ~/saif_pfe
source ~/stt_env/bin/activate
python main.py
```

**Tester avec Zoiper5**
1. Ouvrir Zoiper5 et se connecter avec le compte SIP `1001`
2. Appeler le numéro `700`
3. Après le bip, parler clairement en français
4. Écouter la réponse générée par DENTA (Mistral 7B + TTS)

---

##  5. Tests

### 5.1 Test Vosk (STT)
```bash
cd ~/saif_pfe
source ~/stt_env/bin/activate
python tests/vosk_client_test.py
```

### 5.2 Test Ollama (CLI)
```bash
ollama run mistral "Quels sont vos horaires d'ouverture ?"
```

### 5.3 Test API REST Ollama
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "Bonjour, je voudrais prendre rendez-vous",
    "stream": false
  }'
```

### 5.4 Test scénarios de contexte (158 scénarios)
```bash
cd ~/saif_pfe
source ~/stt_env/bin/activate
python tests/test_context.py
```

### 5.5 Test pipeline complet
```bash
python -c "
from stt.audiosocket_vosk_server import VoiceRecognizer
from llm.ollama_client import ask_mistral
from llm.context_loader import load_scenarios, detect_intent

scenarios = load_scenarios()
print(f'✓ Scénarios chargés : {len(scenarios)}')

reponse = ask_mistral([{'role': 'user', 'content': 'Bonjour'}])
print(f'✓ LLM répond : {reponse[:50]}...')
"
```

---

##  6. Architecture
```
/home/saif/saif_pfe/
├── stt_env/               # Environnement virtuel Python
├── models/                # Modèles Vosk STT
│   ├── vosk-model-fr-0.22.zip          # Production (large)
│   └── vosk-model-small-fr-0.22.zip    # Test rapide
├── stt/
│   └── audiosocket_vosk_server.py
├── llm/
│   ├── __init__.py
│   ├── cabinet_config.py
│   ├── context_loader.py
│   ├── ollama_client.py
│   └── prompt_builder.py
├── tts/
├── tests/
│   ├── vosk_client_test.py
│   ├── debug_server.py
│   └── test_context.py
├── scenarios.csv          # 158 scénarios patient
├── config.py
├── main.py
└── README.md
```

---

##  7. Dépannage

**Ollama not found**
```bash
which ollama
curl -fsSL https://ollama.com/install.sh | sh
```

**Cannot connect to Ollama**
```bash
ps aux | grep ollama
ollama serve
netstat -tulpn | grep 11434
```

**Modèle Mistral non trouvé**
```bash
ollama list
ollama pull mistral
```

**Vosk ne trouve pas le modèle**
```bash
ls -la models/
export VOSK_MODEL_PATH="models/vosk-model-small-fr-0.22"
```

**AudioSocket Connection refused**
```bash
ps aux | grep audiosocket
source ~/stt_env/bin/activate
python stt/audiosocket_vosk_server.py
```

**Zoiper ne se connecte pas**
```bash
sudo netstat -tulpn | grep 5060
tail -f ~/.Zoiper5/zoiper.log
```

**Audio qui ne fonctionne pas**
```bash
arecord -l && aplay -l
arecord -d 5 test.wav && aplay test.wav
```
