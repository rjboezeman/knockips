import geoip2.database
from config import geo_ip_db

class GeoIPLookup:
    def __init__(self, db_path=geo_ip_db):
        self.reader = geoip2.database.Reader(db_path)
        print('GeoIP database loaded.')

    def get_country_by_ip(self, ip_address):
        try:
            response = self.reader.country(ip_address)
            return response.country.name
        except geoip2.errors.AddressNotFoundError:
            return 'Unknown'
        except Exception as e:
            print(f"Error: {e}")
            return 'Unknown'

    def close(self):
        self.reader.close()