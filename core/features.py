from dataclasses import dataclass


@dataclass(frozen=True)
class ProductFeature:
    key: str
    name: str
    status: str
    audience: str
    description: str
    public_enabled: bool = False


FEATURES = {
    "talent_repository": ProductFeature(
        key="talent_repository",
        name="Repositório de talentos",
        status="active",
        audience="Profissionais cabo-verdianos e PALOP",
        description="Pesquisa, perfis públicos, shortlist, comparação e contacto protegido.",
        public_enabled=True,
    ),
    "jobs": ProductFeature(
        key="jobs",
        name="Vagas",
        status="locked",
        audience="Consultorias, empresas e equipas de recrutamento",
        description="Publicação e gestão de vagas preparada para uma fase posterior.",
    ),
    "teams": ProductFeature(
        key="teams",
        name="Equipas de recrutamento",
        status="locked",
        audience="Organizações com vários recrutadores",
        description="Colaboração, notas internas, etiquetas e gestão de pipeline por equipa.",
    ),
    "billing": ProductFeature(
        key="billing",
        name="Planos e cobranças",
        status="locked",
        audience="Empresas que precisam de acesso profissional",
        description="Base para planos, facturação e controlo de acesso sem abertura pública no lançamento.",
    ),
}


def active_features():
    return [feature for feature in FEATURES.values() if feature.public_enabled]


def locked_features():
    return [feature for feature in FEATURES.values() if not feature.public_enabled]
