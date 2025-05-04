import re
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

        self.pricepat_monetary = re.compile("[0-9.,]+.€")
        self.pricepat_plain = re.compile("[0-9.,]+")

    def get_venue_name(self) -> str:
        return self.name

    def get_city(self) -> str:
        return self.city

    def get_country(self) -> str:
        return self.country

    def event_sqlentity(self) -> dict[str, str]:
        return {
            "name": self.name,
            "city": self.city,
            "country": self.country,
        }

    def parse_price(self, info_tag: str) -> str:
        prices_with_mon = self.pricepat_monetary.findall(info_tag)
        prices = []
        for price in prices_with_mon:
            parsed_price = self.pricepat_plain.findall(price)
            if len(parsed_price) == 0:
                continue
            prices.append("".join(parsed_price))

        if len(prices) == 0:
            return "0€"
        elif len(prices) == 2:
            in_advance, from_door = prices[0], prices[1]
            return f"{in_advance}€/{from_door}€"
        return "{}€".format("".join(prices))

    # FIXME Proper class type checking
    def __eq__(self, other):
        return hasattr(other, "url") \
            and other.url == self.url

    @abstractmethod
    def parse_events(self, data: Any) \
            -> Generator[Dict[str, Any], None, None]:
        pass
