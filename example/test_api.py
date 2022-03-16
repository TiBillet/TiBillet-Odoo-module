import requests, json, secret

path_url = 'http://172.17.0.1:8069'


def version():
    url = f'{path_url}/odoo-api/common/version'
    data = {'params': {}}
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.text)
    return r.text


def login():
    url = f'{path_url}/odoo-api/common/login'
    data = {
        'params': {
            'db': f'{secret.database}',
            'login': f'{secret.user}',
            'password': f'{secret.password}',
        }
    }
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.text)


def list_field(model):
    url = f'{path_url}/odoo-api/object/fields_get'
    data = {
        'params': {
            'model': f'{model}',
            'db': f'{secret.database}',
            'login': f'{secret.user}',
            'password': f'{secret.password}',
        }
    }
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.text)
    return r.text

# list_field('res.partner')

def list_entry(model, list_fields: list=None):
    url = f'{path_url}/odoo-api/object/search_read'
    data = {
        'params': {
            'model': f'{model}',
            'db': f'{secret.database}',
            'login': f'{secret.user}',
            'password': f'{secret.password}',
        }
    }
    if list_fields:
        data['params']['keys'] = {'fields':list_fields}

    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.text)
    return  r.text

# list_entry('product.template', ['name','id'])
# list_entry('res.partner', ['name','email','member_lines'])



def create_resPartner(name, email):
    url = f'{path_url}/odoo-api/object/create'

    vals = {
        "name": name,
        "email": email
    }

    data = {
        'params': {
            'model': 'res.partner',
            'vals': vals,
            'db': f'{secret.database}',
            'login': f'{secret.user}',
            'password': f'{secret.password}',
        }
    }
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.text)
