from OdooLocust import OdooLocustUser
from OdooLocust import OdooTaskSet


class Seller(OdooLocustUser.OdooLocustUser):
    database = "testdb"

    tasks = [OdooTaskSet.OdooGenericTaskSet]
