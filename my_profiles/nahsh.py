# my_profiles/nahsh.py
import pytz
from typing import List
from pyhafas.profile import BaseProfile
from pyhafas.profile.base import BaseJourneysRequest
from pyhafas.profile.interfaces.requests.journeys import JourneysRequestInterface
from pyhafas.types.fptf import Journey
from pyhafas.types.hafas_response import HafasResponse


class NahSHJourneysRequest(BaseJourneysRequest, JourneysRequestInterface):
    """
    Parse Nah.SH journeys safely.
    """
    def parse_journeys_request(self, data: HafasResponse) -> List[Journey]:
        journeys = []

        for jny in data.res.get("outConL", []):
            date = self.parse_date(jny["date"])
            journey_id = jny.get("ctxRecon")  # standard in Nah.SH

            if not journey_id:
                continue  # skip malformed journeys

            journeys.append(
                Journey(
                    journey_id,
                    date=date,
                    duration=self.parse_timedelta(jny["dur"]),
                    legs=self.parse_legs(jny, data.common, date),
                )
            )

        return journeys

from datetime import datetime
import pytz
from typing import List
from pyhafas.profile import BaseProfile
from pyhafas.types.fptf import Journey
from pyhafas.types.hafas_response import HafasResponse

class NahSHProfile(BaseProfile):
    baseUrl = "https://nah.sh.hafas.de/bin/mgate.exe"
    locale = "de-DE"
    timezone = pytz.timezone("Europe/Berlin")

    requestBody = {
        "client": {
            "type": "IPH",
            "id": "NAHSH",
            "v": "3000700",
            "name": "NAHSHPROD",
        },
        "auth": {
            "type": "AID",
            "aid": "r0Ot9FLFNAFxijLW",
        },
        "ver": "1.30",
        "lang": "de",
    }

    availableProducts = {
        "nationalExpress": [1],
        "national": [2],
        "interregional": [4],
        "regional": [8],
        "suburban": [16],
        "bus": [32],
        "ferry": [64],
        "subway": [128],
        "tram": [256],
        "onCall": [512],
    }

    defaultProducts = list(availableProducts.keys())

    # --- override journeys parsing to bypass 'ctx' errors ---
    def parse_journeys_request(self, data: HafasResponse) -> List[Journey]:
        journeys = []
        for jny in data.res.get("outConL", []):
            date = self.parse_date(jny["date"])
            journey_id = jny.get("ctxRecon")
            if not journey_id:
                continue
            # minimal journey without legs
            journeys.append(Journey(journey_id, date=date, duration=self.parse_timedelta(jny["dur"]), legs=[]))
        return journeys
