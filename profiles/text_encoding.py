"""Reparação restrita de texto corrompido em importações de perfil conhecidas."""


REPLACEMENTS = {
    "Engenheiro de Petroleo": "Engenheiro de Petróleo",
    "Especialista em Saude Publica": "Especialista em Saúde Pública",
    "Experiencia profissional e colaboracao com projectos ligados a Guine-Bissau.": (
        "Experiência profissional e colaboração com projectos ligados à Guiné-Bissau."
    ),
    "Ligacao profissional confirmada.": "Ligação profissional confirmada.",
    "Guine-Bissau": "Guiné-Bissau",
    "Cat?lica": "Católica",
    "Informa??o": "Informação",
    "informa??o": "informação",
    "Comunica??o": "Comunicação",
    "Transforma??o": "Transformação",
    "transforma??o": "transformação",
    "Gest?o": "Gestão",
    "?gil": "ágil",
    "Guin?-Bissau": "Guiné-Bissau",
    "Tecnol?gicos": "Tecnológicos",
    "Intelig?ncia": "Inteligência",
    "Monitoriza??o": "Monitorização",
    "avalia??o": "avaliação",
    "Ades?o": "Adesão",
    "cria??o": "criação",
    "liga??o": "ligação",
    "colabora??o": "colaboração",
    "Franc?s": "Francês",
    "Ingl?s": "Inglês",
    "Portugu?s": "Português",
    "ligadas ? Guiné-Bissau": "ligadas à Guiné-Bissau",
}


def normalize_text(value):
    for broken, fixed in REPLACEMENTS.items():
        value = value.replace(broken, fixed)
    return value


def normalize_location(value):
    value = normalize_text(value)
    if value.strip().casefold() == "bissau, guiné-bissau".casefold():
        return "Bissau"
    return value


def normalize_value(value):
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    return value


def normalize_profile_snapshot(value):
    value = normalize_value(value)
    if isinstance(value, dict) and "location" in value:
        value["location"] = normalize_location(value["location"])
    return value
