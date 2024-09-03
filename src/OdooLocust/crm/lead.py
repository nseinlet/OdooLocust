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

from datetime import date, timedelta

import names
import random


class CrmLead(OdooTaskSet):
    model_name = 'crm.lead'
    model = False

    def on_start(self):
        super().on_start()
        self.model = self.client.get_model(self.model_name)
        self._load_fields_lists()
        self.test_searchread()

    def _get_search_domain(self):
        if self.filters and random.randint(0, 10) < 3:
            return random.choice(self.filters)
        if random.randint(0, 10) < 6:
            name = names.get_first_name()
            return ['|', '|', '|', ('partner_name', 'ilike', name), ('email_from', 'ilike', name), ('contact_name', 'ilike', name), ('name', 'ilike', name)]
        return super()._get_search_domain()

    @task(10)
    def test_searchread(self):
        search_domains = [
            self._get_search_domain(),
            [('id', '>', self.random_id)],
            []
        ]
        for domain in search_domains:
            res = self.model.search_read(
                domain, 
                self.list_fields,
                limit=80,
                context=self.client.get_user_context()
            )
            if res:
                self.random_id = random.choice(res)['id']
                return True

    @task(5)
    def test_websearchread(self):
        res = self.model.web_search_read(
            specification={f: {} for f in self.list_fields},
            domain=self._get_search_domain(), 
            limit=80,
            context=self.client.get_user_context()
        )
        if res and res['records']:
            self.random_id = random.choice(res['records'])['id']

    @task(20)
    def test_read(self):
        self.model.read(self.random_id, self.form_fields, context=self.client.get_user_context())

    @task(5)
    def lead_stage_change(self):
        s1 = 229
        s2 = 99
        res1 = self.model.search([('id', '>', self.random_id), ('stage_id', '=', s1)], limit=1)
        res2 = self.model.search([('id', '>', self.random_id), ('stage_id', '=', s2)], limit=1)
        if res1:
            self.model.write(res1[0], {'stage_id': s2}, context=self.client.get_user_context())
        if res2:
            self.model.write(res2[0], {'stage_id': s1}, context=self.client.get_user_context())

    @task(5)
    def test_activity(self):
        if self.random_id != -1:
            res_id = self.model.activity_schedule(self.random_id, date_deadline=(date(2012, 1 ,1)+timedelta(days=random.randint(1,3650))).isoformat())
            activity_model = self.client.get_model('mail.activity')
            activity_model.action_done(res_id)

    @task
    def test_pipeline_analysis(self):
        self.model.web_read_group(
            ["&", ["type", "=", "opportunity"], "&", ["create_date", ">=", "2022-01-01 00:00:00"], ["create_date", "<=", "2022-12-31 23:59:59"]],
            ["__count"],
            ["stage_id", "date_deadline:month"],
            context=self.client.get_user_context(),
        )