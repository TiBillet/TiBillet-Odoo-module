# ADD right to user for create membership

## Technical/Show Full Accounting Features
Configuration -> user and society -> groups.
Ajouter l'user dans :

Technique / Montrer les fonctions de comptabilité complètes.
Adhésion / Responsable

# Dev tool within Odoo :

```shell
# edit docker-compose and commit the command. Choose :
command: sleep 30d

# Launch :
docker-compose up -d 

# Go inside the container and install the dev tools
docker exec -ti odoo_web bash
python3 -m pip install ipython ipdb

# launch odoo serveur
bash entrypoint.sh --dev reload

# set in your python code a breakpoint with :
import ipdb; ipdb.set_trace()

# enjoy ipdb !
```


# Know Issues 
##asset bug :

```bash
# https://reedrehg.medium.com/odoo-images-and-attachments-explaining-and-regenerating-assets-d1eb7fe8a3ed

dex <postgres_conteneur>
psql -d postgres -U <USER> -W
\l # liste les bases de données présentes
\c 3Peaks # rentre dans la db odoo
DELETE FROM ir_attachment WHERE url LIKE '/web/content/%';
```

and docker-commpose down & up 
