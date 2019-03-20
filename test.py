from OdooLocust import OdooLocust
from OdooLocust import OdooTaskSet


class Seller(OdooLocust.OdooLocust):
    host = "127.0.0.1"
    database = "testdb"
    min_wait = 100
    max_wait = 1000
    weight = 3
    
    task_set = OdooTaskSet.OdooGenericTaskSet
