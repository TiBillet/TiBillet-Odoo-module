# -*- coding: utf-8 -*-
# TiBillet API Connector
# Ticketing, cashless and cooperative network for artists and organisations.
# Main Dev: Jonas TURBEAUX <contact@tibillet.re>
# TiBillet - https://www.tibillet.re
# Odoo version 15 #


import logging
import re
from datetime import datetime

from odoo import http
from odoo.exceptions import UserError
from odoo.http import Response
import xmlrpc.client
import random
from slugify import slugify

_logger = logging.getLogger(__name__)
CORS = '*'


class TiBilletApi(http.Controller):
    """
    import ipdb; ipdb.set_trace()
    bash entrypoint.sh --dev reload
    common = xmlrpc.client.ServerProxy('http://127.0.0.1:8069/xmlrpc/2/common')
    common.version()
    uid = common.authenticate(db, login, password, {})
    """

    '''
    CLASS INITIALISATION
    '''

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
        self.accounts_journals = {}
        self.curencys = {}

        _logger.info(f"****************************************")
        _logger.info(f"__init__ self.random' : {self.random}")
        _logger.info(f"****************************************")

    '''
    GENERIC FUNCTION
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

    def read(self, model, id=None, fields=None):
        if id == None:
            raise AttributeError('No id in read')
        if fields == None:
            fields = ['name', 'id']
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'read', [id], {'fields': fields})

    def create(self, model, values=None):
        if values is None:
            raise AttributeError('No values for create')
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'create', [values])

    def write(self, model, id, values=None):
        if values is None:
            raise AttributeError('No values for write')
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'write', [[id], values])

    def get_or_create(self, model, filters=None):
        if filters is None:
            filters = []

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
            # Response.status = "409"
            raise KeyError(f"query return {len(query)} objects")

    def action(self, action):
        pass

    '''
    SPECIFIC FUNCTION FOR MEMBERSHIP CREATION
    '''

    def get_or_create_membre(self, membre):
        created = False
        membre_uid = None
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        email = membre['email']
        if not (re.fullmatch(regex, email)):
            raise ValueError(f"{email} not a valid email")

        # assert name and email exist
        name = membre['name']

        query_membre = self.search_read('res.partner', [["email", "=", email]], [])

        if len(query_membre) == 1:
            return query_membre[0]['id'], False
        elif len(query_membre) == 0:
            membre_uid = self.create('res.partner', values=membre)
            return membre_uid, True
        else:
            raise KeyError(f"query with {email} return {len(query_membre)} objects")

    def get_or_create_membership_product(self, adhesion=None):
        if adhesion is None:
            raise AttributeError(f"adhesion must be a json valid with category and product_name")

        category = adhesion["category"]
        product_name = adhesion["product_name"]
        created = False

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
            membership_product, created = self.get_or_create('product.template',
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
        return self.membership_product_id, created

    def get_all_account_journal(self):
        query_account_journal = self.search_read('account.journal', [], ['id', 'name'])
        all_account = {}
        for account in query_account_journal:
            all_account[account.get('name')] = account.get('id')
        self.accounts_journals = all_account
        return all_account

    def get_all_curencys(self):
        query_currency = self.search_read('res.currency', [], ['id', 'name'])
        all_currency = {}
        for curency in query_currency:
            all_currency[curency.get('name')] = curency.get('id')
        self.curencys = all_currency
        return all_currency

    def create_draft_invoice(self, partner_id):
        if not self.accounts_journals.get('Factures clients'):
            self.get_all_account_journal()

        if not self.curencys.get('EUR'):
            self.get_all_curencys()

        values = {
            "currency_id": self.curencys.get('EUR'),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "journal_id": self.accounts_journals.get('Factures clients'),
            "partner_id": partner_id,
            "payment_state": "not_paid",
            "state": "draft",
            "move_type": "out_invoice"
        }

        invoice_draft_id = self.create("account.move", values=values)
        return invoice_draft_id

    def clear_invoice_lines(self, invoice_id=None):
        values = {
            "invoice_line_ids": [
                [5, 0, 0],
            ]
        }
        return self.write('account.move', invoice_id, values)

    def add_product_to_invoice(self, invoice_id=None, product_id=None, price_unit=None, qty=1):
        if invoice_id == None or \
                product_id == None or \
                price_unit == None:
            raise AttributeError(f"add_product_to_invoice attribute error")

        values = {
            "invoice_line_ids": [
                [0, 0, {
                    "move_id": invoice_id,
                    "currency_id": "2",
                    "product_id": product_id,
                    "price_unit": price_unit,
                    "quantity": qty
                }
                 ]
            ]
        }
        return self.write('account.move', invoice_id, values)

    '''
    ACTION
    '''

    def invoice_post(self, invoice_id=None):
        self.models.execute_kw(self.db, self.uid, self.apikey, 'account.move', 'action_post', [[invoice_id]])
        query = self.read('account.move', id=invoice_id, fields=['id', 'state'])
        invoice = query[0]
        return invoice['state']

    def payment(self, invoice_id=None, amount=None, payment_method=None):
        if payment_method is None \
                or not self.accounts_journals.get(payment_method):
            raise AttributeError("payment_method not valid.")

        context = {
            'active_model': 'account.move',
            'active_ids': invoice_id,
        }

        values = {
            'payment_date': datetime.now().strftime("%Y-%m-%d"),
            'journal_id': self.accounts_journals.get(payment_method),
            'amount': amount,
        }
        # 'payment_method_line_id': self.accounts_journals.get(payment_method),  # manual
        # 'amount': amount,

        model_name = 'account.payment.register'
        registered_payment_id = self.models.execute_kw(
            self.db, self.uid, self.apikey, model_name, 'create', [values], {'context': context})

        self.models.execute_kw(
            self.db, self.uid, self.apikey, model_name, 'action_create_payments', [[registered_payment_id]],
            {'context': context})

        query = self.read('account.move', id=invoice_id, fields=['id', 'payment_state'])
        invoice = query[0]

        return invoice['payment_state']

    '''
    AUTH VALIDATOR
    '''

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
                # Response.status = "404"
                raise UserError(f"{group} not find in res.groups")
            if self.uid not in query[0].get('users'):
                # Response.status = "401"
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

        raise UserError('auth failed')

    '''
    API HTTP ROUTING
    '''

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
            # if Response.status == 200:
            #     Response.status = '400'
            return {'status': False, 'error': str(e)}

    # creation d'un nouveau membre
    @http.route('/tibillet-api/xmlrpc/new_membership', type="json", auth='none', cors=CORS, csrf=False)
    def new_membership(self,
                       db=None, login=None, apikey=None,
                       membre=None, adhesion=None,
                       create_invoice=None, set_payment=None,
                       **kw):

        if adhesion is None:
            raise AttributeError("Pas d'adhésion")
        if membre is None:
            raise AttributeError('Pas de membre')

        try:
            uid = self.auth_validator(db, login, apikey)
            membre_uid, created = self.get_or_create_membre(membre)

            invoice_state = "No invoice"
            payment_state = "No payment"
            if create_invoice:
                membership_product_id, pcreated = self.get_or_create_membership_product(adhesion)
                draft_invoice_id = self.create_draft_invoice(membre_uid)

                # clear = self.clear_invoice_lines(draft_invoice_id)

                membership_product_added = self.add_product_to_invoice(
                    invoice_id=draft_invoice_id,
                    product_id=membership_product_id,
                    price_unit=adhesion['price_unit'],
                    qty=1)

                if set_payment:
                    invoice_state = self.invoice_post(draft_invoice_id)

                    payment_state = self.payment(
                        draft_invoice_id,
                        amount=adhesion['price_unit'],
                        payment_method=adhesion['payment_method']
                    )
                else:
                    query = self.read('account.move', id=draft_invoice_id, fields=['id', 'state'])
                    invoice = query[0]
                    invoice_state = invoice['state']

            return {
                "random": self.random,
                "name": membre['name'],
                "email": membre['email'],
                "categorie_saleable_id": self.categorie_saleable_id,
                "membership_category_id": self.membership_category_id,
                "membership_product_id": self.membership_product_id,
                "invoice_state": invoice_state,
                'payment_state': payment_state,
                "responsable": uid,
                "created": created,
                "membre_db": membre_uid
            }

        except Exception as e:
            # if Response.status == 200:
            #     Response.status = '400'
            return {'status': False, 'error': str(e)}
