# OdooLocust

An Odoo load testing solution, using odoolib and Locust. Locust API changed a bit, and OdooLocust follow this change.

## Links

* odoolib: <a href="https://github.com/odoo/odoo-client-lib">odoo-client-lib</a>
* Locust: <a href="http://locust.io">locust.io</a>
* Odoo: <a href="https://odoo.com">odoo.com</a>

# HowTo

To load test Odoo, you create tests like you'll have done it with Locust:

```python
from locust import task, between
from OdooLocust.OdooLocustUser import OdooLocustUser


class Seller(OdooLocustUser):
    wait_time = between(0.1, 10)
    database = "test_db"
    login = "admin"
    password = "secret_password"
    port = 443
    protocol = "jsonrpcs"

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
            'order_line': [(0, 0, {'product_id': prod_ids[0],
                                   'product_uom_qty': 1}),
                           (0, 0, {'product_id': prod_ids[1],
                                   'product_uom_qty': 2}),
                          ]
        })
        so_model.action_button_confirm([order_id])
```

The host on which run the load is defined in locust.conf file, either in your project folder or home folder, as explained in Locust doc:
https://docs.locust.io/en/stable/configuration.html#configuration-file

```
host=localhost
users = 100
spawn-rate = 10
```

then you run your locust tests the usual way:

```bash
locust -f my_file.py
```

# Generic test

This version is shipped with a generic TaskSet task, OdooTaskSet, and a TaskSet which randomly click on menu items,
OdooGenericTaskSet.  To use this version, create this simple test file:

```python
from OdooLocust.OdooLocustUser import OdooLocustUser
from locust import task, between
from OdooLocust import OdooTaskSet


class GenericTest(OdooLocustUser):
    wait_time = between(0.1, 1)
    database = "my_db"
    login = "admin"
    password = "secure_password"
    port = 443
    protocol = "jsonrpcs"

    @task(10)
    def read_partners(self):
        cust_model = self.client.get_model('res.partner')
        cust_ids = cust_model.search([], limit=80)
        prtns = cust_model.read(cust_ids, ['name'])

    tasks = [OdooTaskSet.OdooGenericTaskSet]
```

and you finally run your locust tests the usual way:

```bash
locust -f my_file.py
```

# CRM test

This version is shipped with some CRM tests.

```python
# -*- coding: utf-8 -*-
from OdooLocust import OdooLocustUser, crm

class OdooCom(OdooLocustUser.OdooLocustUser):
    host = "erp.mycompany.com"
    database = "my_db"
    login = "admin"
    password = "secure_password"
    port = 443
    protocol = "jsonrpcs"

    tasks = {crm.partner.ResPartner: 1, crm.lead.CrmLead: 2, crm.quotation.SaleOrder: 1}
```

# Test with workers

As Locust use greenlet, you're using one core of your computer. If this is a limiting factor, it's possible to use multiple workers. It's 
also possible to run a headless test, to automate it. This sh file run a headless test, without asking host, users, ... using an Odoo load 
test file called load_odoo.py:

```bash
#!/bin/bash
if [ -z "$3" ]
  then
      echo "No argument supplied"
      echo "start_workers.sh nbr_workers concurrency time"
      exit 1
fi
x=1
while [ $x -le $1 ]
do
  locust -f load_odoo.py --worker --only-summary > /dev/null 2>&1 &
  x=$(( $x + 1 ))
done
locust -f load_odoo.py --headless --users $2 --spawn-rate $2 --run-time $3m --master --expect-workers=$1
```
