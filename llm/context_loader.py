import csv
import logging
from pathlib import Path

logger = logging.getLogger("ContextLoader")

SCENARIOS_PATH = Path("/home/saif/saif_pfe/scenarios.csv")

KEYWORDS_FALLBACK = {
    "prise_rdv": ["prendre","rendez-vous","rdv","consultation","voir","bilan","controle","detartrage","nettoyage"],
    "prise_rdv_urgence": ["gÃªne","sensible","chaud","froid","manger","dors plus","insupportable","vite","rapide"],
    "urgence": ["urgent","urgence","tres mal","douleur intense","insupportable","nuit","souffre","mal dent"],
    "triage_trauma_avulsion": ["dent tombÃ©e","avulsion","dent arrachÃ©e","dent sortie","dent expulsÃ©e","dans la main"],
    "triage_gonflement_visage": ["gonflement joue","visage enflÃ©","enflure","ballon","joue gonflÃ©e","fiÃ¨vre"],
    "triage_infection_grave": ["gorge enflÃ©e","difficultÃ© avaler","problÃ¨me respiration","phlegmon","Ã©touffe"],
    "postop_saignement": ["saignement","hÃ©morragie","crache sang","sang persistant","extraction dent"],
    "postop_alveolite_douleur": ["alvÃ©olite","douleur extraction","mal aprÃ¨s extraction","trou","lancinant"],
    "annulation": ["annuler","annulation","supprimer","dÃ©commander","pas venir","empÃªchement"],
    "report": ["reporter","dÃ©caler","dÃ©placer","modifier","changer la date","reprogrammer"],
    "attestation_soins": ["attestation","justificatif","document assurance","papier","preuve","mutuelle"],
    "devis_duplicata": ["devis","duplicata","copie devis","devis perdu","renvoi devis","renvoyer"],
    "facture_infos": ["facture","reste Ã  charge","paiement","montant","explication"],
    "modif_coordonnees": ["changement adresse","coordonnÃ©es","dÃ©mÃ©nagement","nouvelle adresse"],
    "envoi_radio": ["radios","radiographie","images","envoyer radios","panoramique"],
    "question_remboursement": ["remboursement","mutuelle","tÃ©lÃ©transmission","CPAM","feuille de soins"],
    "prise_rdv_implantologie": ["implant","implantologie","vis","remplacer dent","dent manquante","trou"],
    "prise_rdv_ortho_enfant": ["orthodontie","bagues","appareil","dents tordues","alignement","fille","fils"],
    "prise_rdv_ortho_adulte": ["orthodontie","adulte","aligner","dents droites","invisalign","aligneurs"],
    "prise_rdv_blanchiment": ["blanchiment","blanchir","Ã©claircissement","dents blanches","esthÃ©tique"],
    "prise_rdv_facettes": ["facettes","hollywood smile","sourire","esthÃ©tique"],
    "prise_rdv_bilan_parodontal": ["gencives","saignent","dÃ©chaussement","bilan parodontal","parodontal"],
    "prise_rdv_prothese_amovible": ["prothÃ¨se","dentier","appareil amovible","fausses dents","rÃ¢telier"],
    "prise_rdv_couronne": ["couronne","prothÃ¨se fixe","cÃ©ramique","empreinte","dent abÃ®mÃ©e"],
    "prise_rdv_referent": ["dentiste m'a envoyÃ©","rÃ©fÃ©rÃ©","orientÃ©","vient de la part","correspondant"],
    "barriere_langue": ["no french","english","don't speak french","language","foreign"],
    "anesthesie_locale": ["grossesse","anesthÃ©sie","enceinte","piqÃ»re"],
    "blanchiment_grossesse": ["grossesse","blanchiment","esthÃ©tique","contre-indication"],
    "refus_peur_douleur": ["peur douleur","phobie dentaire","anxiÃ©tÃ©","crainte","angoisse"],
    "agressivite": ["scandale","agressif","honte","abusÃ©","escroquerie"],
    "verification_nom": ["nom inconnu","fiche introuvable","pas trouvÃ©","comment Ã©crit"],
}

def load_scenarios(path: Path = SCENARIOS_PATH) -> dict:
    scenarios = {}
    if path.is_file():
        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    intent = row.get('intent','').strip()
                    if not intent:
                        continue
                    keywords = [k.strip() for k in row.get('keywords','').split(',') if k.strip()]
                    reponse  = row.get('ia_repond','').strip()
                    cas      = row.get('cas_usage','').strip()
                    if intent not in scenarios:
                        scenarios[intent] = {'reponse': reponse, 'keywords': keywords, 'cas_usage': cas}
                    else:
                        scenarios[intent]['keywords'].extend(keywords)
            logger.info(" %d scÃ©narios chargÃ©s depuis : %s", len(scenarios), path)
        except Exception as e:
            logger.exception("Erreur inattendue lors du chargement CSV : %s", e)
    else:
        logger.warning("  CSV introuvable : %s ? fallback activÃ©", path)
        scenarios = {intent: {'reponse':'', 'keywords':kws, 'cas_usage':''} for intent,kws in KEYWORDS_FALLBACK.items()}
        logger.info(" %d intents fallback chargÃ©s", len(scenarios))
    return scenarios

def detect_intent(text: str, scenarios: dict) -> str:
    text_lower = text.lower()
    for intent, data in scenarios.items():
        if any(kw.lower() in text_lower for kw in data['keywords'] if kw):
            logger.debug("Intent dÃ©tectÃ© : %s", intent)
            return intent
    logger.debug("Aucun intent dÃ©tectÃ© ? UNKNOWN")
    return "UNKNOWN"

def get_context_hint(text: str, scenarios: dict) -> str:
    text_lower = text.lower()
    for intent, data in scenarios.items():
        if any(kw.lower() in text_lower for kw in data['keywords'] if kw):
            hint = f"[Intent:{intent}]"
            if data['reponse']:
                hint += f" [Suggestion:{data['reponse']}]"
            logger.debug("Hint contexte : %s", hint[:80])
            return hint
    return ""