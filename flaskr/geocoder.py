import geopy
import shelve
import time


class CachedGeocoder:
    def __init__(self, source="Nominatim", geocache="geocache.db"):
        self.geocoder = getattr(geopy.geocoders, source)()
        self.cache = shelve.open(geocache, writeback=True)
        self.timestamp = time.time() + 1.5

    def geocode(self, address):
        if address not in self.cache:
            time.sleep(max(0, 1 - (time.time() - self.timestamp)))
            self.timestamp = time.time()
            self.cache[address] = self.geocoder.geocode(address)
        return self.cache[address]