# OdooLocust

An Odoo load testing solution, using openerplib and Locust

## Links

* openerplib: <a href="https://github.com/nicolas-van/openerp-client-lib">openerp-client-lib</a>
* Locust: <a href="http://locust.io">locust.io</a>
* Odoo: <a href="https://odoo.com">odoo.com</a>

# HowTo

To load test Odoo, you create tasks sets like you'll have done it with Locust:

```
from locust import task, TaskSet

class SellerTaskSet(TaskSet):
    @task(10)
    def read_partners(self):
        cust_model = self.client.get_model('res.partner')
        cust_ids = cust_model.search([])
        prtns = cust_model.read(cust_ids)
        
    @task(5)
    def read_products(self):
        prod_model = self.client.get_model('product.product')
        ids = prod_model.search([])
        prods = prod_model.read(ids)
        
    @task(20)
    def create_so(self):
        prod_model = self.client.get_model('product.product')
        cust_model = self.client.get_model('res.partner')
        so_model = self.client.get_model('sale.order')
        
        cust_id = cust_model.search([('name', 'ilike', 'fletch')])[0]
        prod_ids = prod_model.search([('name', 'ilike', 'ipad')])
        
        order_id = so_model.create({
            'partner_id': cust_id,
            'order_line': [(0,0,{'product_id': prod_ids[0], 
                                 'product_uom_qty':1}),
                           (0,0,{'product_id': prod_ids[1], 
                                 'product_uom_qty':2}),
                          ],
            
        })
        so_model.action_button_confirm([order_id,])
```

then you create a profile, based on your taskset, which use OdooLocust instead of Locust:

```
from OdooLocust import OdooLocust
from SellerTaskSet import SellerTaskSet

class Seller(OdooLocust):
    host = "127.0.0.1"
    database = "test_db"
    min_wait = 100
    max_wait = 1000
    weight = 3
    
    task_set = SellerTaskSet
```

and you finally run your locust tests the usual way:

```
locust -f my_file.py Seller
```
