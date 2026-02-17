from locust import task, between
from OdooLocust.OdooLocustUser import OdooLocustUser


class Seller(OdooLocustUser):
    wait_time = between(0.1, 10)
    database = "test_db"
    login = "admin"
    password = "secret_password"
    port = 443
    protocol = "json2s"
    
    @task(10)
    def read_partners(self):
        cust_model = self.client.get_model('res.partner')
        cust_ids = cust_model.search(domain=[])
        prtns = cust_model.read(cust_ids)

    @task(5)
    def read_products(self):
        prod_model = self.client.get_model('product.product')
        ids = prod_model.search(domain=[])
        prods = prod_model.read(ids)

    @task(20)
    def create_so(self):
        prod_model = self.client.get_model('product.product')
        cust_model = self.client.get_model('res.partner')
        so_model = self.client.get_model('sale.order')

        cust_id = cust_model.search(domain=[('name', 'ilike', 'fletch')])[0]
        prod_ids = prod_model.search(domain=[('name', 'ilike', 'ipad')])

        order_id = so_model.create(vals_list = {
            'partner_id': cust_id,
            'order_line': [(0, 0, {'product_id': prod_ids[0],
                                   'product_uom_qty': 1}),
                           (0, 0, {'product_id': prod_ids[1],
                                   'product_uom_qty': 2}),
                          ]
        })
        so_model.action_confirm([order_id])
