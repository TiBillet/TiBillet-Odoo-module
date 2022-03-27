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

# Usefull Doc :

https://gist.github.com/101t/3982252740ce44d3affba37edea6ed33#file-deployment-guide-to-installing-odoo-14-on-ubuntu-20-04-md

https://reedrehg.medium.com/odoo-images-and-attachments-explaining-and-regenerating-assets-d1eb7fe8a3ed

# Know Issues 
##asset bug :

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


