import geoip2.database
from config import geo_ip_country_db, geo_ip_city_db, geo_ip_asn_db
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
    def __init__(self, country_db_path=geo_ip_country_db, city_db_path=geo_ip_city_db, asn_db_path=geo_ip_asn_db):
        self.do_country = True
        self.do_city = True
        self.do_asn = True
        # check if file exists:
        if len(str(country_db_path)) == 0 or not os.path.isfile(country_db_path):
            log.warning(f"GeoIP country database '{country_db_path}' is not a valid MMDB file. Skipping country check.")
            self.do_country = False
        else:
            try:
                self.country_reader = geoip2.database.Reader(country_db_path)
                log.info(f"GeoIP country database loaded: {country_db_path}")
            except Exception as e:
                log.error(f"{e} Skipping country check.")
                self.do_country = False
        if len(str(city_db_path)) == 0 or not os.path.isfile(city_db_path):
            log.warning(f"GeoIP city database '{city_db_path}' is not a valid MMDB file. Skipping city check.")
            self.do_city = False
        else:
            try:
                self.city_reader = geoip2.database.Reader(city_db_path)
                log.info(f"GeoIP city database loaded: {city_db_path}")
            except Exception as e:
                log.error(f"{e} Skipping city check.")
                self.do_city = False
        if len(str(asn_db_path)) == 0 or not os.path.isfile(asn_db_path):
            log.warning(f"GeoIP ASN database '{asn_db_path}' is not a valid MMDB file. Skipping ASN check.")
            self.do_asn = False
        else:
            try:
                self.asn_reader = geoip2.database.Reader(asn_db_path)
                log.info(f"GeoIP ASN database loaded: {asn_db_path}")
            except Exception as e:
                log.error(f"{e} Skipping ASN check.")
                self.do_asn = False

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

    def get_asn_by_ip(self, ip_address):
        try:
            if not self.do_asn:
                return 'No data'
            response = self.asn_reader.asn(ip_address)
            return response.autonomous_system_number
        except geoip2.errors.AddressNotFoundError:
            return 'Unknown'
        except Exception as e:
            log.error(f"Error: {e}")
            return 'Unknown'
        
    def get_asn_organization_by_ip(self, ip_address):
        try:
            if not self.do_asn:
                return 'No data'
            response = self.asn_reader.asn(ip_address)
            return response.autonomous_system_organization
        except geoip2.errors.AddressNotFoundError:
            return 'Unknown'
        except Exception as e:
            log.error(f"Error: {e}")
            return

    def close(self):
        if self.do_country:
            self.country_reader.close()
        if self.do_city:
            self.city_reader.close()