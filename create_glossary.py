import requests
import os

# Set up DeepL API Key
api_key = os.getenv('DEEPL_API_KEY')

# Define glossary terms
glossary_terms = {
    "##": "##",
    "end-cap": "end-cap",
    "barrel": "barrel",
    "jet": "jet",
    "jets": "jets",
    "transverse momentum": "momento transverso",
    "pileup": "pileup",
    "pile-up": "pileup",
    "decay": "decaimiento",
    "tile": "tile",
    "trigger": "trigger",
    "acceptance": "aceptancia",
    "efficiency": "eficiencia",
    "track": "traza",
    "hit": "hit",
    "missing transverse momentum": "momento transverso faltante",
    "online": "online",
    "offline": "offline",
    "run": "run",
    "confidence level": "nivel de confianza",
    "beamline": "tubo del haz",
    "crack": "crack",
    "loose": "loose",
    "tight": "tight",
    "prompt": "prompt",
    "grid": "grilla",
    "background": "fondo",
    "likelihood": "likelihood",
    "sample": "muestra",
    "branching ratio": "branching ratio",
}

# Format glossary for the API
glossary_entries = "\n".join([f"{src_term}\t{tgt_term}" for src_term, tgt_term in glossary_terms.items()])

# Create a glossary via DeepL API
response = requests.post(
    'https://api-free.deepl.com/v2/glossaries',
    data={
        'name': 'GlossaryOne',
        'source_lang': 'EN',
        'target_lang': 'ES',
        'entries_format': 'tsv',
        'entries': glossary_entries,
    },
    headers={'Authorization': f'DeepL-Auth-Key {api_key}'}
)

# Check if the glossary was successfully created
if response.status_code == 200:
    glossary_id = response.json()["glossary_id"]
    print(f"Glossary created with ID: {glossary_id}")
else:
    print(f"Failed to create glossary: {response.status_code}, {response.text}")


# GlossaryOne   8207f4a4-d59e-48bf-b6a8-311565268d06