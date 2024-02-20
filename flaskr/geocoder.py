import shelve
import ssl
import time

import certifi
import geopy
import geopy.geocoders

from flaskr.core import get_path

ssl_ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ssl_ctx


class CachedGeocoder:

    def __init__(self, source="Nominatim", geocache="geocache.db"):
        self.geocoder = getattr(geopy.geocoders, source)(
            scheme='https',
            user_agent='TravelCarbonFootprintCalculator',
        )
        self.cache = shelve.open(get_path(geocache), writeback=True)

    def geocode(self, address):
        if address not in self.cache:
            time.sleep(1.618)
            self.cache[address] = self.geocoder.geocode(
                query=address,
                timeout=5,
                # language='en_US',  # buggy since 2024
                language='en',
                addressdetails=True,  # only works with Nominatim /!.
            )
        return self.cache[address]

    def __del__(self):
        self.close()

    def close(self):
        self.cache.close()
