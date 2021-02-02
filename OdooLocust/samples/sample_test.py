from OdooLocust import OdooLocust
from SellerTaskSet import SellerTaskSet


class Seller(OdooLocust):
    host = "127.0.0.1"
    database = "test_db"
    min_wait = 100
    max_wait = 1000
    weight = 3

    task_set = SellerTaskSet
