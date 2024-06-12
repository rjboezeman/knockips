import geoip2.database
from config import geo_ip_country_db, geo_ip_city_db
from utils.logger import log

class SingletonMeta(type):
    """
    This is a metaclass for Singleton pattern.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class GeoIPLookup(metaclass=SingletonMeta):
    def __init__(self, country_db_path=geo_ip_country_db, city_db_path=geo_ip_city_db):
        self.country_reader = geoip2.database.Reader(country_db_path)
        self.city_reader = geoip2.database.Reader(city_db_path)
        log.info('GeoIP database(s) loaded.')

    def get_country_by_ip(self, ip_address):
        try:
            response = self.country_reader.country(ip_address)
            return response.country.name
        except geoip2.errors.AddressNotFoundError:
            return 'Unknown'
        except Exception as e:
            log.error(f"Error: {e}")
            return 'Unknown'
    
    def get_city_by_ip(self, ip_address):
        try:
            response = self.city_reader.city(ip_address)
            return response.city.name
        except geoip2.errors.AddressNotFoundError:
            return 'Unknown'
        except Exception as e:
            log.error(f"Error: {e}")
            return 'Unknown'

    def close(self):
        self.reader.close()