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
    list_fields = ["activity_exception_decoration", "activity_exception_icon", "activity_state", "activity_summary", "activity_type_icon", "activity_type_id", "name", "create_date", "commitment_date", "expected_date", "partner_id", "website_id", "user_id", "activity_ids", "team_id", "tag_ids", "company_id", "amount_untaxed", "amount_tax", "amount_total", "state", "validity_date", "invoice_status", "message_needaction", "currency_id"]
    form_fields = ["authorized_transaction_ids", "is_subscription", "enterprise_is_new_plan", "state", "subscription_management", "is_upselling", "stage_category", "end_date", "archived_product_count", "partner_credit_warning", "project_ids", "is_product_milestone", "project_count", "milestone_count", "tasks_count", "timesheet_count", "timesheet_total_duration", "timesheet_encode_uom_id", "expense_count", "delivery_count", "id", "planning_first_sale_line_id", "planning_initial_date", "planning_hours_to_plan", "planning_hours_planned", "invoice_count", "attendee_count", "event_booth_count", "history_count", "recurring_monthly", "mrp_production_count", "database_count", "payment_exception", "to_renew", "renew_state", "name", "partner_id", "commission_plan_frozen", "referrer_id", "commission_plan_id", "delivery_set", "is_all_service", "recompute_delivery_price", "sale_order_template_id", "validity_date", "date_order", "recurrence_id", "invoice_date_diff", "next_invoice_date", "expected_next_invoice_date", "show_update_pricelist", "pricelist_id", "company_id", "currency_id", "tax_country_id", "payment_term_id", "new_sub_id", "old_sub_id", "order_line", "is_avatax", "note", "tax_totals", "commission", "sale_order_option_ids", "user_id", "team_id", "website_id", "is_abandoned_cart", "cart_recovery_email_sent", "require_signature", "require_payment", "website_description", "reference", "client_order_ref", "tag_ids", "start_date", "first_contract_date", "avatax_unique_code", "show_update_fpos", "fiscal_position_id", "partner_invoice_id", "analytic_account_id", "visible_project", "project_id", "invoice_status", "commercial_partner_id", "payment_token_id", "warehouse_id", "picking_policy", "commitment_date", "expected_date", "show_json_popover", "json_popover", "effective_date", "delivery_status", "origin", "campaign_id", "medium_id", "source_id", "internal_note", "enterprise_final_customer_id", "enterprise_security_email", "is_staff_restricted", "subscription_tag_ids", "enterprise_saas", "upsell_order_id", "upsell_date", "upsell_content", "maintenance_subscription_id", "maintenance_main_subscription_id", "maintenance_is_activated", "maintenance_stage_category", "odoo_sh_extra_gb", "odoo_sh_extra_stagings", "odoo_sh_extra_workers", "odoo_sh_extra_dedicated", "exclude_dashboard", "github_user_ids", "is_taxcloud", "is_taxcloud_configured", "display_name"]
    line_fields = ["analytic_precision", "sequence", "display_type", "product_uom_category_id", "product_type", "product_updatable", "product_id", "product_template_id", "product_template_attribute_value_ids", "product_custom_attribute_value_ids", "product_no_variant_attribute_value_ids", "is_configurable_product", "event_id", "event_ticket_id", "is_event_booth", "event_booth_category_id", "event_booth_pending_ids", "name", "temporal_type", "website_description", "analytic_distribution", "product_uom_qty", "qty_delivered", "virtual_available_at_date", "qty_available_today", "free_qty_today", "scheduled_date", "forecast_expected_date", "warehouse_id", "move_ids", "qty_to_deliver", "is_mto", "display_qty_widget", "qty_delivered_method", "qty_invoiced", "qty_to_invoice", "product_uom_readonly", "product_uom", "customer_lead", "recompute_delivery_price", "is_delivery", "price_unit", "tax_id", "price_tax", "discount", "is_downpayment", "price_subtotal", "state", "invoice_status", "currency_id", "company_id", "database_id", "computation"]
    random_id = 2795659

    @task
    def test_list(self):
        name = names.get_first_name()
        saleorder_model = self.client.get_model('sale.order')
        for domain in ([], ["|", "|", ["name", "ilike", name], ["client_order_ref", "ilike", name], ["partner_id", "child_of", name]]) :
            res = saleorder_model.web_search_read(
                domain,
                self.list_fields,
                limit=80,
                context=self.client.get_user_context(),
            )
            if res and domain:
                self.random_id = res[0]['id']

    @task
    def test_form(self):
        saleorder_model = self.client.get_model('sale.order')
        saleorderline_model = self.client.get_model('sale.order.line')
        res = saleorder_model.read(
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
        saleorder_model = self.client.get_model('sale.order')
        saleorder_model.action_draft([self.random_id], context=self.client.get_user_context())

    @task
    def test_quotation_confirm(self):
        saleorder_model = self.client.get_model('sale.order')
        res = saleorder_model.search([['state', '=', 'draft'], '!', [ 'order_line.product_id.active', '=', False ], [ 'partner_id.country_id', '!=', False], [ 'company_id', '=', 1]], context=self.client.get_user_context())
        saleorder_model.action_confirm(random.choice(res), context=self.client.get_user_context())

    @task
    def test_quotation_sendemail(self):
        saleorder_model = self.client.get_model('sale.order')
        saleorder_model.action_quotation_send([self.random_id], context=self.client.get_user_context())
