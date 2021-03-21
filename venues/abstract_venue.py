from abc import ABC, abstractmethod
from typing import Any, Dict, Generator


class IncorrectVenueImplementation(Exception):
    pass


# class AbstractVenue(metaclass=ABC):
class AbstractVenue(ABC):
    def __init__(self):
        self.url = ""
        self.name = ""
        self.city = ""
        self.country = ""

    def get_venue_name(self) -> str:
        return self.name

    def get_city(self) -> str:
        return self.city

    def get_country(self) -> str:
        return self.country

    def event_sqlentity(self) -> Dict[str, str]:
        return {"name": self.name,
                "city": self.city,
                "country": self.country}

    @abstractmethod
    def parse_events(self, data: Any) \
            -> Generator[Dict[str, Any], None, None]:
        pass
