from OdooLocust import OdooLocustUser
from OdooLocust import OdooTaskSet


class Seller(OdooLocustUser.OdooLocustUser):
    database = "testdb"
    cookies = {
        'tz': 'Europe/Brussels',
    }

    tasks = [OdooTaskSet.OdooGenericTaskSet]
