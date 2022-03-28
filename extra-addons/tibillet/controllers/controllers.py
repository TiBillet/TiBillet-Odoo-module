# -*- coding: utf-8 -*-
# TiBillet API Connector
# Ticketing, cashless and cooperative network for artists and organisations.
# Main Dev: Jonas TURBEAUX <contact@tibillet.re>
# TiBillet - https://www.tibillet.re
import logging
from datetime import datetime

import odoo
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request, Response
import re
import xmlrpc.client
import random
from slugify import slugify

_logger = logging.getLogger(__name__)
CORS = '*'


class TiBilletApi(http.Controller):
    # version 0.1 #
    '''
    import ipdb; ipdb.set_trace()
    bash entrypoint.sh --dev reload
    common = xmlrpc.client.ServerProxy('http://127.0.0.1:8069/xmlrpc/2/common')
    common.version()
    uid = common.authenticate(db, login, password, {})
    '''

    common = xmlrpc.client.ServerProxy('http://127.0.0.1:8069/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy('http://127.0.0.1:8069/xmlrpc/2/object')

    def list_all(self, model, fields):
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'search_read', [],
                                      {'fields': fields})

    def search_read(self, model, filters, fields):
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'search_read', [filters],
                                      {'fields': fields})

    def get_fields(self, model):
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'fields_get', [],
                                      {'attributes': ['string', 'help', 'type']})

    def read(self, model, ids):
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'read', ids, {'fields': ['name', 'id']})

    def create(self, model, values=None):
        if values is None:
            raise AttributeError('No values for create')
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'create', [values])

    def get_or_create(self, model, filters=[]):
        query = self.search_read(model, filters, ['id'])
        if len(query) == 1:
            _logger.info(f"FOUND {model} : {query[0]}")
            return query[0]['id'], False
        elif len(query) == 0:
            values = {}
            for filter in filters:
                values[filter[0]] = filter[2]
            _logger.info(f"CREATE with : {values}")
            id = self.create(model, values=values)
            return id, True
        else:
            Response.status = "409"
            raise KeyError(f"query return {len(query)} objects")

    def get_or_create_membre(self, membre):
        created = False
        membre_uid = None

        # assert name and email exist
        email = membre['email']
        name = membre['name']

        query_membre = self.search_read('res.partner', [["email", "=", email]], [])

        if len(query_membre) == 1:
            Response.status = '409'
            raise UserError("Email exist")
        elif len(query_membre) == 0:
            membre_uid = self.create('res.partner', values=membre)
            created = True
        else:
            Response.status = "409"
            raise KeyError(f"query with {email} return {len(query_membre)} objects")

        return membre_uid, created

    def get_or_create_membership_product(self, adhesion):
        category = adhesion["category"]
        product_name = adhesion["product_name"]

        # get categorie product
        if not self.categorie_saleable_id:
            categorie_saleable = self.search_read('product.category', [['name', '=', 'Saleable']], ['id'])
            self.categorie_saleable_id = categorie_saleable[0].get('id')

        # TODO: utiliser setattrib pour créer des self id par category et product name
        if not self.membership_category_id:
            membership_category, db_created = self.get_or_create('membership.membership_category',
                                                                 [['name', '=', category]])
            self.membership_category_id = membership_category

        if not self.membership_product_id:
            membership_product, db_created = self.get_or_create('product.template',
                                                                [
                                                                    ['name', '=', product_name],
                                                                    ['membership', '=', True],
                                                                    ['categ_id', '=', self.categorie_saleable_id],
                                                                    ['detailed_type', '=', 'service'],
                                                                    ['membership_type', '=', 'variable'],
                                                                    ['membership_interval_qty', '=', 1],
                                                                    ['membership_category_id', '=',
                                                                     self.membership_category_id],
                                                                ])
            self.membership_product_id = membership_product
        return self.membership_product_id

    def create_draft_invoice(self, partner_id):
        if not self.eur_currency_id:
            eur_currency = self.search_read('res.currency', [['name', '=', 'EUR']], ['id'])
            self.eur_currency_id = eur_currency[0].get('id')

        if not self.account_journal_id:
            account_journal = self.search_read('account.journal', [['name', '=', 'Factures clients']], ['id'])
            self.account_journal_id = account_journal[0].get('id')

        values = {
            "currency_id": self.eur_currency_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "journal_id": self.account_journal_id,
            "partner_id": partner_id,
            "payment_state": "not_paid",
            "state": "draft",
            "move_type": "out_invoice"
        }

        return self.create("account.move", values=values)

    def __init__(self):
        super().__init__()
        self.random = str(random.random())
        self.db = None
        self.login = None
        self.apikey = None

        '''
        USEFUL VARIABLE FOR DB OPTIMISATION
        '''
        # Permissions de groupes
        self.show_full_accounting_features = None
        self.manager = None
        self.categorie_saleable_id = None
        self.membership_category_id = None
        self.membership_product_id = None
        self.eur_currency_id = None
        self.account_journal_id = None

        _logger.info(f"******************************")
        _logger.info(f"__init__ self.random' : {self.random}")
        _logger.info(f"******************************")

    def user_permission_validator(self):
        if self.show_full_accounting_features and self.manager:
            _logger.info(f'show_full_accounting_features : {self.show_full_accounting_features}')
            _logger.info(f'manager : {self.manager}')

            return True

        for group in \
                ['Technical / Show Full Accounting Features', 'Membership / Manager']:

            query = self.search_read(
                model='res.groups',
                filters=[["full_name", "=", group]],
                fields=["name", "users"]
            )
            if len(query) != 1:
                Response.status = "404"
                raise UserError(f"{group} not find in res.groups")
            if self.uid not in query[0].get('users'):
                Response.status = "401"
                raise UserError(f"User's Permission not in {group}")

            group_name = slugify(query[0].get('name')).replace('-', '_')
            setattr(self, group_name, query[0].get('id'))

        return True

    def auth_validator(self, db, login, apikey):
        uid = self.common.authenticate(db, login, apikey, {})
        if uid:
            self.uid = uid
            self.db = db
            self.login = login
            self.apikey = apikey
            self.user_permission_validator()

        return uid

    # Check version
    @http.route('/tibillet-api/common/version', type="json", auth='none', cors=CORS)
    def version(self, **kw):
        version = self.common.version()
        version['random'] = self.random
        return version

    # login
    @http.route('/tibillet-api/xmlrpc/login', type="json", auth='none', cors=CORS)
    def login(self, db=None, login=None, apikey=None, **kw):
        try:
            uid = self.auth_validator(db, login, apikey)
            # another way :
            # uid = request.session.authenticate(db, login, password)
            return {
                "random": self.random,
                "user_uid": uid,
                "authentification": bool(uid),
                "permissions":
                    {
                        "show_full_accounting_features": self.show_full_accounting_features,
                        "manager": self.manager
                    }
            }
        except Exception as e:
            if Response.status == 200:
                Response.status = '400'
            return {'status': False, 'error': str(e)}

    # creation d'un nouveau membre
    @http.route('/tibillet-api/xmlrpc/new_membership', type="json", auth='none', cors=CORS)
    def new_membership(self, db=None, login=None, apikey=None, membre={}, adhesion={}, **kw):
        try:
            uid = self.auth_validator(db, login, apikey)
            membre_uid, created = self.get_or_create_membre(membre)

            self.membership_product_id = self.get_or_create_membership_product(adhesion)

            draft_invoice_id = self.create_draft_invoice(membre_uid)

            return {
                "random": self.random,
                "categorie_saleable_id": self.categorie_saleable_id,
                "membership_category_id": self.membership_category_id,
                "membership_product_id": self.membership_product_id,
                "eur_currency_id": self.eur_currency_id,
                "account_journal_id": self.account_journal_id,
                "draft_invoice_id": draft_invoice_id,
                "responsable": uid,
                "created": created,
                "membre_db": membre_uid
            }

        except Exception as e:
            if Response.status == 200:
                Response.status = '400'
            return {'status': False, 'error': str(e)}
