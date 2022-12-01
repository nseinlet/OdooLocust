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

from locust import task, TaskSet


class OdooTaskSet(TaskSet):
    def _get_user_context(self):
        res = self.client.get_model('res.users').read(self.client.user_id, ['lang', 'tz'])
        return {
            'uid': self.client.user_id,
            'lang': res['lang'],
            'tz': res['tz'],
        }

    def _fields_view_get(self, model, view_mode):
        res = self.client.get_model(model).load_views(views=[(False, vm) for vm in list(set(["list", "form", "search", view_mode]))])
        return [n for n in res.get('fields_views', {}).get(view_mode, {}).get('fields', {}).keys()]

    def _filters_view_get(self, model):
        res = self.client.get_model(model).load_views(views=[(False, vm) for vm in list(set(["list", "form", "search"]))])
        return [n['domain'] for n in res.get('filters', {})]

    def _parse_children_menu(self, childs):
        res = []
        for child in childs:
            if child['action']:
                res.append(child['action'].split(","))
            if child['children']:
                res += self._parse_children_menu(child['children'])
        return res

    def _load_menu(self):
        res = self.client.get_model('ir.ui.menu').load_menus(False, context=self._get_user_context())
        return self._parse_children_menu(res['children'])

    def _action_load(self, action_id, action_type=None):
        if not action_type:
            base_action = self.client.get_model('ir.actions.actions').read(action_id, ['type'])
            action_type = base_action[0]['type']
        return self.client.get_model(action_type).read(action_id, [])


class OdooGenericTaskSet(OdooTaskSet):

    def on_start(self):
        self.menu = self._load_menu()
        self.randomlyChooseMenu()

    @task(1)
    def randomlyChooseMenu(self):
        self.model = False
        while not self.model and self.model != "False":
            item = random.choice(self.menu)
            self.last_action = self._action_load(int(item[1]), item[0])
            self.model = self.last_action.get('res_model', False)
        self.form_fields = self._fields_view_get(self.model, "form")
        self.list_fields = self._fields_view_get(self.model, "list")
        if "kanban" in self.last_action.get('view_mode', []):
            self.kanban_fields = self._fields_view_get(self.model, "kanban")
        self.filters = self._filters_view_get(self.model)

    @task(30)
    def form_view(self):
        domain = []
        if self.filters and random.randint(0, 10) < 3:
            domain = random.choice(self.filters)
        context = self.client.get_user_context()
        model = self.client.get_model(self.model)
        nbr_records = model.search_count(domain or [], context=context)
        offset = random.randint(0, nbr_records % 80) if nbr_records > 80 else 0
        ids = model.search(domain or [], limit=80, offset=offset, context=context)
        if ids:
            model.read(random.choice(ids), self.form_fields, context=context)

    @task(10)
    def list_view(self):
        domain = []
        if self.filters and random.randint(0, 10) < 3:
            domain = random.choice(self.filters)
        context = self.client.get_user_context()
        model = self.client.get_model(self.model)
        nbr_records = model.search_count(domain or [], context=context)
        ids = model.search(domain or [], limit=80)
        if nbr_records > 80:
            offset = random.randint(0, nbr_records % 80)
            ids = model.search(domain or [], limit=80, offset=offset, context=context)
        if ids:
            model.search_read([('id', 'in', ids)], self.list_fields, context=context)

    @task(10)
    def kanban_view(self):
        if "kanban" in self.last_action.get('view_mode', []):
            domain = []
            if self.filters and random.randint(0, 10) < 3:
                domain = random.choice(self.filters)
            context = self.client.get_user_context()
            model = self.client.get_model(self.model)
            nbr_records = model.search_count(domain or [], context=context)
            ids = model.search(domain or [], limit=80)
            if nbr_records > 80:
                offset = random.randint(0, nbr_records % 80)
                ids = model.search(domain or [], limit=80, offset=offset, context=context)
            if ids:
                model.search_read([('id', 'in', ids)], self.kanban_fields, context=context)
