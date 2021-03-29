import geopy
import shelve
import time

from flaskr.core import get_path


class CachedGeocoder:

    def __init__(self, source="Nominatim", geocache="geocache.db"):
        self.geocoder = getattr(geopy.geocoders, source)()
        self.cache = shelve.open(get_path(geocache), writeback=True)
        # self.timestamp = time.time() + 1.5

    def geocode(self, address):
        if address not in self.cache:
            # time.sleep(max(0, 1 - (time.time() - self.timestamp)))
            time.sleep(1.618)
            # self.timestamp = time.time()
            self.cache[address] = self.geocoder.geocode(
                query=address,
                timeout=5,
                language='en_US',  # urgh
                addressdetails=True,  # only works with Nominatim /!.
            )
        return self.cache[address]

    def close(self):
        self.cache.close()
