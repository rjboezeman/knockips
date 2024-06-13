import geoip2.database
from config import geo_ip_country_db, geo_ip_city_db
from utils.logger import log
import os

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
        self.do_country = True
        self.do_city = True
        # check if file exists:
        if len(str(country_db_path)) == 0 or not os.path.isfile(country_db_path):
            log.warning(f"GeoIP country database '{country_db_path}' is not a valid MMDB file. Skipping country check.")
            self.do_country = False
        else:
            try:
                self.country_reader = geoip2.database.Reader(country_db_path)
                log.info('GeoIP country database loaded.')
            except Exception as e:
                log.error(f"{e} Skipping country check.")
                self.do_country = False
        if len(str(city_db_path)) == 0 or not os.path.isfile(city_db_path):
            log.warning(f"GeoIP city database '{city_db_path}' is not a valid MMDB file. Skipping city check.")
            self.do_city = False
        else:
            try:
                self.city_reader = geoip2.database.Reader(city_db_path)
                log.info('GeoIP city database loaded.')
            except Exception as e:
                log.error(f"{e} Skipping city check.")
                self.do_city = False

    def get_country_by_ip(self, ip_address):
        try:
            if not self.do_country:
                return 'No data'
            response = self.country_reader.country(ip_address)
            return response.country.name
        except geoip2.errors.AddressNotFoundError:
            return 'Unknown'
        except Exception as e:
            log.error(f"Error: {e}")
            return 'Unknown'
    
    def get_city_by_ip(self, ip_address):
        try:
            if not self.do_city:
                return 'No data'
            response = self.city_reader.city(ip_address)
            return response.city.name
        except geoip2.errors.AddressNotFoundError:
            return 'Unknown'
        except Exception as e:
            log.error(f"Error: {e}")
            return 'Unknown'

    def close(self):
        self.reader.close()