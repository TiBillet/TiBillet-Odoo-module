# -*- coding: utf-8 -*-
# TiBillet API Connector
# Ticketing, cashless and cooperative network for artists and organisations.
# Main Dev: Jonas TURBEAUX <contact@tibillet.re>
# TiBillet - https://www.tibillet.re
import logging
import odoo
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
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

    def search_read(self, model, key, value, fields):
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'search_read', [[[key, '=', value]]],
                                      {'fields': fields})

    def get_fields(self, model):
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'fields_get', [], {'attributes': ['string', 'help', 'type']})

    def read(self, model, ids):
        return self.models.execute_kw(self.db, self.uid, self.apikey, model, 'read', ids, {'fields': ['name', 'id']})


    def __init__(self):
        super().__init__()
        self.random = str(random.random())
        self.db = None
        self.login = None
        self.apikey = None

        # On va chercher les permissions de groupes
        self.show_full_accounting_features = None
        self.manager = None

        _logger.info(f"******************************        __init__ self.common : {self.common}")

    def validator_user_permission(self):
        if self.show_full_accounting_features and self.manager :
            _logger.info(f'show_full_accounting_features : {self.show_full_accounting_features}')
            _logger.info(f'manager : {self.manager}')

            return True

        for group in \
                ['Technical / Show Full Accounting Features','Membership / Manager']:

            query = self.search_read(
                model='res.groups',
                key="full_name",
                value=group,
                fields=["name", "users"]
            )
            if len(query) != 1 :
                raise UserError("Technical / Show Full Accounting Features or not Membership / Manager not find in res.groups")
            if self.uid not in query[0].get('users') :
                raise UserError("User's Permission not Technical / Show Full Accounting Features or not Membership / Manager")

            group_name = slugify(query[0].get('name')).replace('-','_')
            setattr(self,group_name, query[0].get('id'))

        return True

    def validator(self, db, login, apikey):
        uid = self.common.authenticate(db, login, apikey, {})
        self.uid = uid
        self.db = db
        self.login = login
        self.apikey = apikey
        self.validator_user_permission()

        return uid

    # Check version
    @http.route('/tibillet-api/common/version', type="json", auth='none', cors=CORS)
    def version(self, **kw):
        version = self.common.version()
        version['random'] = self.random
        return version

    # login #
    @http.route('/tibillet-api/common/login', type="json", auth='none', cors=CORS)
    def login_http(self, db=None, login=None, password=None, **kw):
        try:
            # uid = self.common.authenticate(db, login, password, {})
            # another way :
            uid = request.session.authenticate(db, login, password)
            return {
                "user_uid": uid,
                "authentification": True
            }
        except Exception as e:
            return {'status': False, 'error': str(e)}

    # login #
    @http.route('/tibillet-api/xmlrpc/login', type="json", auth='none', cors=CORS)
    def login_xmlrpc(self, db=None, login=None, apikey=None, **kw):
        try:
            uid = self.common.authenticate(db, login, apikey, {})
            # another way :
            # uid = request.session.authenticate(db, login, password)
            return {
                "random": self.random,
                "user_uid": uid,
                "authentification": True,
                "permissions":
                    {
                        "comptabilite_complete": self.res_groups_comptabilite_complete_uid,
                        "adhesion_responsable": self.res_groups_adhesion_responsable_uid
                    }
            }
        except Exception as e:
            return {'status': False, 'error': str(e)}

    # login #
    @http.route('/tibillet-api/xmlrpc/new_membership', type="json", auth='none', cors=CORS)
    def login_xmlrpc(self, db=None, login=None, apikey=None, **kw):
        try:
            uid = self.validator(db, login, apikey)
            return {
                "responsable": uid,
                "new_membre": True
            }

        except Exception as e:
            return {'status': False, 'error': str(e)}
