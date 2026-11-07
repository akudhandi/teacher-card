"""Fixed demo personas per country.

Deterministic inputs so demo and test output is reproducible across runs.
Each persona carries the person fields only; the school is resolved from the
country's own school list at generation time (the first entry, unless a school
name is supplied explicitly).
"""

from typing import Dict, Optional

# country code -> persona
PERSONAS: Dict[str, Dict[str, str]] = {
    "us": {"first": "John", "last": "Smith", "position": "Head of Science Department", "dob": "12/05/1988", "gender": "Male"},
    "uk": {"first": "Emily", "last": "Turner", "position": "Head of English Department", "dob": "03/09/1985", "gender": "Female"},
    "france": {"first": "Camille", "last": "Laurent", "position": "Professeur de Mathématiques", "dob": "21/02/1987", "gender": "Female"},
    "netherlands": {"first": "Daan", "last": "de Vries", "position": "Docent Natuurkunde", "dob": "14/06/1983", "gender": "Male"},
    "indonesia": {"first": "Budi", "last": "Santoso", "position": "Guru Matematika", "dob": "07/04/1986", "gender": "Male"},
    "australia": {"first": "Olivia", "last": "Bennett", "position": "Head of Science Department", "dob": "19/11/1984", "gender": "Female"},
    "canada": {"first": "Liam", "last": "Tremblay", "position": "Head of Mathematics Department", "dob": "02/08/1982", "gender": "Male"},
    "spain": {"first": "Lucía", "last": "García", "position": "Jefa de Departamento de Ciencias", "dob": "30/01/1986", "gender": "Female"},
    "argentina": {"first": "Sofía", "last": "Fernández", "position": "Jefa de Departamento de Lengua", "dob": "11/03/1988", "gender": "Female"},
    "slovakia": {"first": "Martin", "last": "Horváth", "position": "Učiteľ matematiky", "dob": "25/07/1981", "gender": "Male"},
    "mexico": {"first": "Diego", "last": "Ramírez", "position": "Jefe de Departamento de Ciencias", "dob": "09/12/1985", "gender": "Male"},
    "philippines": {"first": "Maria", "last": "Santos", "position": "Head of Science Department", "dob": "17/05/1987", "gender": "Female"},
    "thailand": {"first": "Somchai", "last": "Jaidee", "position": "Head of Science Department", "dob": "08/10/1983", "gender": "Male"},
}

DEFAULT_PERSONA = {
    "first": "Alex",
    "last": "Morgan",
    "position": "Head of Science Department",
    "dob": "01/01/1985",
    "gender": "Random",
}


def get_persona(country: str, name: Optional[str] = None) -> Dict[str, str]:
    """Return a persona for a country.

    Args:
        country: Country code.
        name: Optional persona key to look up; falls back to the country's
            built-in persona, then DEFAULT_PERSONA.
    """
    if name and name in PERSONAS:
        return dict(PERSONAS[name])
    return dict(PERSONAS.get(country, DEFAULT_PERSONA))
