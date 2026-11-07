"""
Base classes for country-specific document generators
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from pathlib import Path
import random


class CountryGenerator(ABC):
    """Base class for country-specific document generators"""
    
    def __init__(self):
        self.schools = self._load_schools()
        self.first_names = self.get_first_names()
        self.last_names = self.get_last_names()
        self.positions = self.get_positions()
    
    @abstractmethod
    def get_country_name(self) -> str:
        """Return the country name"""
        pass
    
    @abstractmethod
    def get_country_code(self) -> str:
        """Return the country code (e.g., 'uk', 'france')"""
        pass
    
    @abstractmethod
    def get_schools_data(self) -> List[Dict]:
        """Return list of schools"""
        pass
    
    @abstractmethod
    def get_first_names(self) -> List[str]:
        """Return list of first names"""
        pass
    
    @abstractmethod
    def get_last_names(self) -> List[str]:
        """Return list of last names"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[str]:
        """Return list of teaching positions"""
        pass
    
    @abstractmethod
    def get_document_types(self) -> List[str]:
        """Return list of available document types"""
        pass
    
    @abstractmethod
    def generate_document(self, doc_type: str, first: str, last: str, 
                         school: Dict, position: str, dob: str) -> bytes:
        """Generate a specific document type"""
        pass
    
    def _load_schools(self) -> List[Dict]:
        """Load schools from JSON or return default data"""
        data_dir = Path(__file__).parent.parent.parent / "data"
        json_path = data_dir / f"{self.get_country_code()}_schools.json"
        
        if json_path.exists():
            try:
                import json
                return json.loads(json_path.read_text())
            except:
                pass
        
        return self.get_schools_data()
    
    def random_school(self) -> Dict:
        """Get a random school"""
        return random.choice(self.schools)
    
    def search_school(self, query: str) -> Dict:
        """Search for a school by name"""
        query_lower = query.lower()
        for school in self.schools:
            if query_lower in school["name"].lower():
                return school
        return None
    
    def list_schools(self) -> List[str]:
        """List all school names"""
        return [s["name"] for s in self.schools]
    
    def generate_name(self) -> Tuple[str, str]:
        """Generate a random name"""
        return random.choice(self.first_names), random.choice(self.last_names)
    
    def random_position(self) -> str:
        """Get a random teaching position"""
        return random.choice(self.positions)

    def generate_document_seeded(self, doc_type: str, first: str, last: str,
                                 school: Dict, position: str, dob: str,
                                 seed=None, watermark: bool = False,
                                 watermark_text: str = None, fmt: str = "png",
                                 quality: int = 90, dpi: int = 300,
                                 photo_path: str = None) -> bytes:
        """Generate one document with optional deterministic seeding, watermarking and format.

        Args:
            seed: When set, the RNG is seeded from this value plus the document
                type and person, so identical inputs yield byte-identical output
                (ignoring date fields). When None, the global RNG is left alone.
            watermark: When True, stamps a "SAMPLE" banner over the result.
            watermark_text: Overrides the default banner text.
            fmt: Output format — 'png', 'jpg', or 'pdf'.
            quality: JPEG quality, ignored for other formats.
            dpi: Resolution embedded in PDF output.
            photo_path: Optional explicit profile photo file for this person,
                overriding the bundled photo pool.
        """
        from .utils import set_active_photo, validate_dob

        for label, value in (("first_name", first), ("last_name", last), ("position", position)):
            if not (value or "").strip():
                raise ValueError(f"{label} is required.")

        dob = validate_dob(dob)

        set_active_photo(photo_path)

        if seed is not None:
            random.seed(f"{seed}:{doc_type}:{first}:{last}")

        data = self.generate_document(doc_type, first, last, school, position, dob)

        if watermark:
            from .utils import finalize_document
            data = finalize_document(data, watermark=True, text=watermark_text)

        if fmt and fmt.lower().lstrip(".") not in ("png",):
            from .utils import encode_document
            data = encode_document(data, fmt=fmt, quality=quality, dpi=dpi)

        return data
