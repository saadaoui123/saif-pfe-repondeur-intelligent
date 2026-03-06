
CABINET = {
    'nom_cabinet'             : 'Cabinet Dentaire',
    'jours_ouverture'         : ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi'],
    'horaires_ouverture'      : {'debut': 9, 'fin': 18},
    'jours_secretaire'        : ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi'],
    'horaires_secretaire'     : {'debut': 9, 'fin': 17},
    'urgence_externe'         : False,
    'urgence_garde'           : '09 705 00 205',
    'politique_douleur_interne': 'J+0 ou J+1',
    'politique_douleur_externe': '48h',
    'liste_specialites'       : [
        'implantologie',
        'orthodontie enfant',
        'orthodontie adulte',
        'parodontologie',
        'chirurgie parodontale',
        'protheses amovibles',
        'protheses fixes',
        'soins esthetiques',
        'blanchiment',
        'facettes dentaires',
        'detartrage',
        'controle',
        'scanner dentaire',
        'soins post-operatoires',
        'soins pour femmes enceintes',
    ],
    'actes_esthetiques'       : True,
    'scanner_present'         : True,
    'protheses_amovibles'     : True,
    'protheses_fixes'         : True,
    'paro_chirurgicale'       : True,
    'prise_rdv_en_ligne'      : True,
    'politique_retard'        : '10 minutes',
    'politique_annulation'    : '48h de prÃ©avis',
    'envoi_radios'            : True,
    'adresse_envoi_radios'    : 'contact@cabinetdentaire.fr',
    'paiement_differe'        : True,
    'mode_paiement_acceptes'  : ['CB', 'cheque', 'especes'],
    'acceptation_enfants'     : True,
}


import textwrap

def build_context(cabinet: dict) -> str:
    """Construit le bloc de contexte cabinet pour le system prompt."""
    return textwrap.dedent(f"""
    CONTEXTE CABINET:
    - Horaires      : LundiÂVendredi {cabinet['horaires_ouverture']['debut']}h00Â{cabinet['horaires_ouverture']['fin']}h00. FermÃ© le week-end.
    - SecrÃ©tariat   : {cabinet['horaires_secretaire']['debut']}h00Â{cabinet['horaires_secretaire']['fin']}h00
    - Urgences internes (patients connus)   : {cabinet['politique_douleur_interne']}
    - Urgences externes (nouveaux patients) : orienter garde dentaire {cabinet['urgence_garde']}
    - Services pratiquÃ©s : {', '.join(cabinet['liste_specialites'])}
    - Paiements     : {', '.join(cabinet['mode_paiement_acceptes'])} Â paiement diffÃ©rÃ© acceptÃ©
    - Annulation    : prÃ©avis {cabinet['politique_annulation']}
    - Retard tolÃ©rÃ© : {cabinet['politique_retard']}
    - Envoi radios  : par email ? {cabinet['adresse_envoi_radios']}
    - Enfants mineurs : acceptÃ©s
    """).strip()
