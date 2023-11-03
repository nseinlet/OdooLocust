# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) Stephane Wirtel
# Copyright (C) 2011 Nicolas Vanhoren
# Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
# Copyright (C) 2017 Nicolas Seinlet
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
import odoolib
import time
import sys

from locust import HttpUser, events


def send(self, service_name, method, *args):
    if service_name == "object" and method == "execute_kw":
        call_name = "%s : %s" % args[3:5]
    else:
        call_name = '%s : %s' % (service_name, method)
    start_time = time.time()
    try:
        res = odoolib.json_rpc(self.url, "call", {"service": service_name, "method": method, "args": args})
    except Exception as e:
        total_time = int((time.time() - start_time) * 1000)
        events.request.fire(request_type="OdooRPC", name=call_name, response_time=total_time, response_length=0, exception=e)
        raise e
    else:
        total_time = int((time.time() - start_time) * 1000)
        events.request.fire(request_type="OdooRPC", name=call_name, response_time=total_time, response_length=sys.getsizeof(res))
        return res


odoolib.JsonRPCConnector.send = send
odoolib.JsonRPCSConnector.send = send


class OdooLocustUser(HttpUser):
    abstract = True
    port = 8069
    database = "demo"
    login = "admin"
    password = "admin"
    protocol = "jsonrpc"
    user_id = -1

    def on_start(self):
        user_id = None
        if self.user_id and self.user_id > 0:
            user_id = self.user_id
        self.client = odoolib.get_connection(hostname=self.host,
                                             port=self.port,
                                             database=self.database,
                                             login=self.login,
                                             password=self.password,
                                             protocol=self.protocol,
                                             user_id=user_id)
        self.client.check_login(force=False)
