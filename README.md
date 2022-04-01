# Odoo
Odoo for TiBillet financial report

# RoadMap :
- [x] XMLRPX http API
- [x] API Création de fiche contact Odoo
- [x] Nouvelle adhésion TiBillet -> Odoo

# API :

Postman documentation : https://documenter.getpostman.com/view/17519122/UVypzHCa

### Version :

	POST http://localhost:8069/tibillet-api/common/version

####BODY
```json
{
    "params": {}
}
```

#### RESPONSE
```json
{
    "jsonrpc": "2.0",
    "id": null,
    "result": {
        "server_version": "15.0-20220307",
        "server_version_info": [
            15,
            0,
            0,
            "final",
            0,
            ""
        ],
        "server_serie": "15.0",
        "protocol_version": 1,
        "random": "0.5241139307469328"
    }
}
```



# Install :

## From scratch :


```
git clone --recurse-submodules https://github.com/TiBillet/Odoo.git
```

Copier le fichier ```docker/env_example``` vers ```docker/.env```.
Modifiez le fichier ```.env``` pour changer les variables.

Lancez ```docker-compose config``` pour vérifier que tout est bon.
Créez le réseau comme indiqué si besoin.


Lancez les conteneurs : ```docker-compose up -d```

Aller sur ```http://localhost:8069``` et suivez les instructions.
Notez bien le mot de passe master, il ne vous sera plus présenté nulle part.
Notez aussi le nom que vous avez donné à la base de donnée odoo.

## Avec un Odoo 15 déjà installé

Copiez et/ou montez ces dossier dans le dossier addon de votre installation.

- extra-addons/tibillet:/mnt/extra-addons/tibillet
- submodule/odoo_api:/mnt/extra-addons/odoo_api
- submodule/vertical-association/membership_extension:/mnt/extra-addons/membership_extension
- submodule/vertical-association/membership_variable_period:/mnt/extra-addons/membership_variable_period

## Inside Odoo

Allez sur Odoo / Application. Retirez le tag "application" dans la barre de recherche. Tapez "tibillet" et installez.
Cela va vérifier si les application suivantes sont installées et les installer si besoin.

```
# __manifest__.py
'depends': [
    'base',
    'account',
    'contacts',
    'membership',
    'membership_extension',
    'membership_variable_period',
    'odoo_api'
], 
```

