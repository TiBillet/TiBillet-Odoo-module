# Odoo

Odoo connexion for TiBillet environment
https://www.tibillet.re
https://github.com/TiBillet

# RoadMap :

- [x] XMLRPX http API
- [x] Api Check Version
- [x] Api Check Login
- [x] API Création de fiche contact Odoo
- [x] Nouvelle adhésion TiBillet -> Odoo
- [x] Utilise le contact existant avec même email
- [x] Création d'un nouvel article d'adhésion s'il n'existe pas
- [ ] Gestion des périodes d'adhésion ( pour l'instant : 365j )
- [x] Facturation en brouillon de l'adhésion
- [x] Validation de la facture
- [x] Paiement de la facture
- [x] Selection du moyen de paiement ( Doit être account.journal. A indiquer dans la configuration de l'instance cashless )
- [ ] Création des moyens de paiements manquant ( account.journal )
- [ ] Connexion avec le module POS ( point de vente )
- [ ] Ajout de chaque article vendu dans TiBillvet -> Odoo
- [ ] Gestion de la monnaie dans compte et journaux Odoo
- [ ] Ajout de la monnaie cashless dans les POS
- [ ] Interfaçage des boitiers lecteurs NFC TiBillet dans POS Odoo
- [ ] Accepter les monnaies cashless dans POS Odoo

# API :

Postman documentation : https://documenter.getpostman.com/view/17519122/UVypzHCa

## Version :

	POST http://localhost:8069/tibillet-api/common/version

#### POST DATA

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

## Login :

	POST http://localhost:8069/tibillet-api/xmlrpc/login

#### Parameters

| Attribute | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| `db`      | string | yes      | Odoo server DB name |
| `login`   | string | yes      | Odoo User           |
| `api_key` | string | yes      | Odoo User ApiKey    |

#### POST DATA

```json
{
  "params": {
    "db": "{{db}}",
    "login": "{{login}}",
    "apikey": "{{api_key}}"
  }
}
```

#### Response :

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "random": "0.7985724403682478",
    "user_uid": 2,
    "authentification": true,
    "permissions": {
      "show_full_accounting_features": 25,
      "manager": 31
    }
  }
}
```

## Nouvelle Adhésion

	POST http://localhost:8069/tibillet-api/xmlrpc/new_membership/

#### Parameters

| Attribute                 | Type   | Required | Description                                                         |
|---------------------------|--------|----------|---------------------------------------------------------------------|
| `db`                      | string | yes      | Odoo server DB name                                                 |
| `login`                   | string | yes      | Odoo User                                                           |
| `api_key`                 | string | yes      | Odoo User ApiKey                                                    |
| `create_invoice`          | bool   | no       | Crée une facture en brouillon           |
| `set_payment`             | bool   | no       | Valide la facture et créé un paiement                               |
| `membre:name`             | string | yes      | Nom / Prenom                                                        |
| `membre:email`            | string | yes      | Si email existe déja, utilise le contact existant.                  |
| `adhesion:product_name`   | string | yes      | Nom de l'adhésion                                                   |
| `adhesion:category`       | string | yes      | Tag odoo "Catégorie d'adhésion" visible sur la fiche de l'adhérant. |
| `adhesion:price_unit`     | string | yes      | Tarif de l'adhésion.                                                |
| `adhesion:payment_method` | string | yes      | Type de paiement. str : account.journal                             |

#### POST DATA

```json
{
  "params": {
    "db": "{{db}}",
    "login": "{{login}}",
    "apikey": "{{api_key}}",
    "create_invoice": true,
    "set_payment": true,
    "membre": {
      "name": "{{$randomFirstName}} {{$randomLastName}}",
      "email": "{{$randomEmail}}"
    },
    "adhesion": {
      "product_name": "Adhésion",
      "category": "Adhérant",
      "price_unit": 52,
      "payment_method": "Espèces"
    }
  }
}
```

#### Response :

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "random": "0.5980815715295654",
    "name": "Eldora Hansen",
    "email": "Leilani22@hotmail.com",
    "categorie_saleable_id": 2,
    "membership_category_id": 2,
    "membership_product_id": 1,
    "invoice_state": "posted",
    "payment_state": "paid",
    "responsable": 2,
    "created": true,
    "membre_db": 145
  }
}
```

# Install :

Need :

- Linux
- Odoo V15
- docker
- docker-compose V3
- Traefik ( for reverse-proxy )

## From scratch :

```
git clone --recurse-submodules git@github.com:TiBillet/TiBillet-Odoo-module.git
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

Copiez et/ou montez ces dossiers dans le dossier addon de votre installation.

- extra-addons/tibillet:/mnt/extra-addons/tibillet
- submodule/vertical-association/membership_extension:/mnt/extra-addons/membership_extension
- submodule/vertical-association/membership_variable_period:/mnt/extra-addons/membership_variable_period

## Inside Odoo

### Installer l'addon

Allez sur Odoo / Application. Retirez le tag "application" dans la barre de recherche. Tapez "tibillet" et installez.
Cela va vérifier si les applications suivantes sont installées et les installer si besoin.

```
# __manifest__.py
'depends': [
    'base',
    'account',
    'contacts',
    'membership',
    'membership_extension',
    'membership_variable_period',
], 
```

### Créer une clé d'api

https://www.odoo.com/documentation/15.0/developer/misc/api/odoo.html#api-keys

### Configurer le Cashless de TiBillet

Dans l'interface admin -> Configuration Générale -> Onglet ODOO.
Renseignez les champs obligatoires.

Vous pouvez choisir de ne pas activer l'envoie vers Odoo, de ne créer que des factures en brouillon, ou des factures
validées et payées.

```Last log odoo:``` Vous montre la validité de la dernière action.

## Configurer le Cashless

## Testez l'API et l'Authentification

```shell
curl --location --request POST 'http://localhost:8069/tibillet-api/xmlrpc/login' \
--data-raw '{
    "params": {
        "db": "${ODOO_DATABASE}",
        "login": "${LOGIN}>",
        "apikey": "${API_KEY}"
    }
}'
```

### Permissions :

Si None dans les permissions :

```json
"permissions": {
  "show_full_accounting_features": None,
  "manager": none
}
```

Rajoutez les droits d'utilisateur dans Odoo :
Paramètres -> utilisateurs et sociétés -> Groupes

- Technique / Montrer les fonctions de comptabilité complètes
- Adhésion / Responsable

# Development environment 

## Tips : Python Breakpoint

```shell
# edit docker-compose and commit the command. Choose :
command: sleep 30d

# Launch :
docker compose up -d 

# Go inside the container and install the dev tools
docker exec -ti odoo_web bash
python3 -m pip install ipython ipdb

# launch odoo serveur
bash entrypoint.sh --dev reload
```

```python
# set in your python code a breakpoint with :
import ipdb; ipdb.set_trace()

# enjoy ipdb !
```

### Usefull Doc :

https://gist.github.com/101t/3982252740ce44d3affba37edea6ed33#file-deployment-guide-to-installing-odoo-14-on-ubuntu-20-04-md

https://reedrehg.medium.com/odoo-images-and-attachments-explaining-and-regenerating-assets-d1eb7fe8a3ed

# Know Issues 

## asset bug :

```bash

# see bashrc for detail
docker exec -ti odoo_web reload_asset <ODOO_DB_NAME>
```

You can also simply prevent Odoo from using the filestore 
by setting the system parameterir_attachment.location to 
```db-storage in Settings->Parameters->System Parameters ```.
(requires technical features).

and restart :
```docker-commpose restart```

# AUTHORS

Jonas TURBEAUX for TiBillet ( https://www.tibillet.re )

# THANKS & SPONSORS

- La Raffinerie

https://www.laraffinerie.re
 
[![logo La Raffinerie](https://documentation.laraffinerie.re/images/thumb/c/c3/LogoRaffinerie.png/300px-LogoRaffinerie.png)](https://www.laraffinerie.re)

- Communnecter.org

https://www.communecter.org

[![logo Communnecter](https://www.communecter.org/assets/94396c20/images/logos/logo-full.png)](https://www.communecter.org)

- JetBrain

https://jb.gg/OpenSourceSupport

![logo JetBrain](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg)


- @ibuioli Ignacio Buioli for his XMLRPC API example for inspiration : https://github.com/codize-app/odoo_api