# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2022 Nicolas Seinlet
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################

from ..OdooTaskSet import OdooTaskSet
from locust import task

import names
import random

class SaleOrder(OdooTaskSet):
    line_fields = []
    model_name = 'sale.order'

    def on_start(self):
        super().on_start()
        self.model = self.client.get_model(self.model_name)
        self._load_fields_lists()
        self.line_fields = self._fields_view_get('sale.order.line', 'list')
        self.test_list()

    def _get_search_domain(self):
        if self.filters and random.randint(0, 10) < 3:
            return random.choice(self.filters)
        if random.randint(0, 10) < 6:
            name = names.get_first_name()
            return ["|", "|", ["name", "ilike", name], ["client_order_ref", "ilike", name], ["partner_id", "child_of", name]]
        return super()._get_search_domain()

    @task
    def test_list(self):
        search_domains = [
            self._get_search_domain(),
            [('id', '>', self.random_id)],
            []
        ]
        for domain in search_domains:
            res = self.model.web_search_read(
                specification={f: {} for f in self.list_fields},
                domain=domain,
                limit=80,
                context=self.client.get_user_context(),
            )
            if res and res['records']:
                self.random_id = random.choice(res['records'])['id']
                return True

    @task
    def test_form(self):
        if self.random_id != -1:
            saleorderline_model = self.client.get_model('sale.order.line')
            res = self.model.read(
                [self.random_id],
                self.form_fields,
                context=self.client.get_user_context(),
            )
            saleorderline_model.search_read(
                [ ['order_id', '=', self.random_id] ],
                self.line_fields,
                context=self.client.get_user_context(),
            )

    @task
    def test_set_to_quotation(self):
        if self.random_id != -1:
            self.model.action_draft([self.random_id], context=self.client.get_user_context())

    @task
    def test_quotation_confirm(self):
        res = self.model.search([['state', '=', 'draft'], '!', [ 'order_line.product_id.active', '=', False ], [ 'partner_id.country_id', '!=', False], [ 'company_id', '=', 1]], context=self.client.get_user_context())
        if res:
            self.random_id = random.choice(res)
            self.model.action_confirm(random.choice(res), context=self.client.get_user_context())

    @task
    def test_quotation_sendemail(self):
        if self.random_id != -1:
            self.model.action_quotation_send([self.random_id], context=self.client.get_user_context())

    @task(5)
    def new_quotation(self):
        prtn_model = self.client.get_model('res.partner')
        prod_model = self.client.get_model('product.product')
        prtn_cnt = prtn_model.search_count([])
        prod_cnt = prod_model.search_count([('sale_ok', '=', True)])

        prtn_id = prtn_model.search([], offset=random.randint(0, prtn_cnt - 1), limit=1)

        so_lines = []
        for i in range(0, random.randint(1, 10)):
            prod_id = prod_model.search([('sale_ok', '=', True)], offset=random.randint(0, prod_cnt - 1), limit=1)
            so_lines.append((0, 0, {'product_id': prod_id[0], }))

        self.random_id = self.model.create({
            'partner_id': prtn_id[0],
            'order_line': so_lines,
        })
