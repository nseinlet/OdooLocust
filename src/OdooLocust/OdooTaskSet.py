# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2019 Nicolas Seinlet
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
import random
import names

from locust import task, TaskSet


class OdooTaskSet(TaskSet):
    model_name = False
    model = False
    form_fields = []
    list_fields = []
    kanban_fields = []
    filters = []
    random_id = -1

    def on_start(self):
        super().on_start()
        if self.model_name:
            self.model = self.client.get_model(self.model_name)

    def _get_user_context(self):
        res = self.client.get_model('res.users').read(self.client.user_id, ['lang', 'tz'])
        return {
            'uid': self.client.user_id,
            'lang': res['lang'],
            'tz': res['tz'],
        }

    def _fields_view_get(self, model, view_mode):
        res = self.client.get_model(model).get_views(views=[(False, vm) for vm in list(set(["list", "form", "search", view_mode]))])
        return [n for n in res.get('fields_views', {}).get(view_mode, {}).get('fields', {}).keys()]

    def _filters_view_get(self, model):
        res = self.client.get_model(model).get_views(views=[(False, vm) for vm in list(set(["list", "form", "search"]))])
        return [n['domain'] for n in res.get('filters', {})]

    def _load_menu(self):
        menus = []
        res = self.client.get_model('ir.ui.menu').load_menus(False, context=self._get_user_context())
        for menu_id in res.keys():
            menu = res[menu_id].get('action')
            if menu:
                menus.append(menu.split(","))
        return menus

    def _action_load(self, action_id, action_type=None):
        if not action_type:
            base_action = self.client.get_model('ir.actions.actions').read(action_id, ['type'])
            action_type = base_action[0]['type']
        return self.client.get_model(action_type).read(action_id, [])
    
    def _check_fields(self, model, fields_list):
        all_fields = self.client.get_model(model).fields_get()
        return [ f for f in fields_list if f in all_fields.keys() ]
    
    def _load_fields_lists(self, form=True, list=True, kanban=False, filters=True):
        self.form_fields = self._fields_view_get(self.model_name, "form") if form else []
        self.list_fields = self._fields_view_get(self.model_name, "list") if list else []
        self.kanban_fields = self._fields_view_get(self.model_name, "kanban") if kanban else []
        self.filters = self._filters_view_get(self.model_name) if filters else []

    def _get_search_domain(self):
        if self.filters and random.randint(0, 10) < 3:
            return random.choice(self.filters)
        if 'name' in self.list_fields and random.randint(0, 10) < 6:
            name = names.get_first_name()
            return [('name', 'ilike', name)]
        return []


class OdooGenericTaskSet(OdooTaskSet):
    # def on_start(self):
    #     super().on_start()
    #     self.menu = self._load_menu()
    #     self.randomlyChooseMenu()

    # @task(1)
    def randomlyChooseMenu(self):
        self.model_name = False
        self.model = False
        while not self.model_name and self.model_name != "False":
            item = random.choice(self.menu)
            self.last_action = self._action_load(int(item[1]), item[0])
            self.model_name = self.last_action.get('res_model', False)
        self.model = self.client.get_model(self.model_name)
        self._load_fields_lists(kanban="kanban" in self.last_action.get('view_mode', []))

    @task(10)
    def test_search(self):
        ids = self.model.search(self._get_search_domain(), context=self.client.get_user_context(), limit=80)
        if ids:
            self.random_id = random.choice(ids)
    
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

    @task(30)
    def form_view(self):
        domain = self._get_search_domain()
        context = self.client.get_user_context()
        nbr_records = self.model.search_count(domain, context=context)
        offset = random.randint(0, nbr_records % 80) if nbr_records > 80 else 0
        ids = self.model.search(domain, limit=80, offset=offset, context=context)
        if ids:
            self.random_id = random.choice(ids) 
        if self.random_id:
            self.model.read(self.random_id, self.form_fields, context=context)

    @task(10)
    def list_view(self):
        domain = self._get_search_domain()
        context = self.client.get_user_context()
        ids = self.model.search(domain, limit=80, context=context)
        nbr_records = self.model.search_count(domain, context=context)
        if nbr_records > 80:
            self.model.read(ids, self.list_fields, context=context)
            offset = random.randint(0, nbr_records % 80)
            ids = self.model.search(domain, limit=80, offset=offset, context=context)
        if ids:
            self.model.read(ids, self.list_fields, context=context)

    @task(10)
    def kanban_view(self):
        if self.kanban_fields:
            domain = self._get_search_domain()
            context = self.client.get_user_context()
            ids = self.model.search(domain, limit=80, context=context)
            nbr_records = self.model.search_count(domain, context=context)
            if nbr_records > 80:
                self.model.read(ids, self.kanban_fields, context=context)
                offset = random.randint(0, nbr_records % 80)
                ids = self.model.search(domain, limit=80, offset=offset, context=context)
            if ids:
                self.model.read(ids, self.kanban_fields, context=context)
