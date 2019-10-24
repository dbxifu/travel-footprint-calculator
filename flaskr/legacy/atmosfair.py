import json

import requests


# Sample file for getting data out of atmosfair,
# to be refactored as a Driver somehow.
# This is not used as-is in this project.


def request_info_atmosfair_de(from_airport, to_airport):
    json_value = {
        "amount": 0,
        "returnFlight": True,
        "flightCount": 1,
        "passengerCount": 1,
        "entireAircraft": False,
        "legs": [{
            "airport": json.loads(from_airport)[0],
            "travelClass": None, "charter": None,
            "aircraft": None
        }, {
            "airport": json.loads(to_airport)[0],
            "travelClass": None, "charter": None,
            "aircraft": None
        }],
        "proportion": 1
    }
    #    print(json_value)
    r = requests.post(
        'https://co2offset.atmosfair.de/api/flight/activity',
        json=json_value
    )
    return r


def request_airport_atmosfair_de(code_aita):
    r = requests.get(
        "https://co2offset.atmosfair.de/api/airport",
        "query=" + code_aita
    )
    return r


if __name__ == '__main__':
    from_airport = request_airport_atmosfair_de("CDG")
    to_airport = request_airport_atmosfair_de("IAD")

    r = request_info_atmosfair_de(from_airport.text, to_airport.text)
    print(r.text)
    print(r.json().get('co2'))
    print(r.json().get('rfi'))
    print(r.json().get('legs'))
    airlineemissions = r.json().get('airlineEmissions')
    print airlineemissions
