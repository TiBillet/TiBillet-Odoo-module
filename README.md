# Odoo
Odoo for TiBillet financial report

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
- [ ] Selection du moyen de paiement ( actuellement uniquement Espèce )
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
            15, 0, 0, "final", 0, ""
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
| `create_invoice`          | bool   | no       | Crée une factured e l'adhésion en brouillon avec si True            |
| `set_payment`             | bool   | no       | Valide la facture et créé un paiement                               |
| `membre:name`             | string | yes      | Nom / Prenom                                                        |
| `membre:email`            | string | yes      | Si email existe déja, utilise le contact existant.                  |
| `adhesion:product_name`   | string | yes      | Nom de l'adhésion                                                   |
| `adhesion:category`       | string | yes      | Tag odoo "Catégorie d'adhésion" visible sur la fiche de l'adhérant. |
| `adhesion:price_unit`     | string | yes      | Tarif de l'adhésion.                                                |
| `adhesion:payment_method` | string | yes      | Type de paiement. Accèpte uniquement : Espèce / Banque                  |

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
```js
        "permissions": {
            "show_full_accounting_features": None,
            "manager": none
        }
```

Rajoutez les droits d'utilisateur dans Odoo :
Paramètres -> utilisateurs et sociétés -> Groupes
- Technique / Montrer les fonctions de comptabilité complètes
- Adhésion / Responsable