# Docker install on linux

```console
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
sudo systemctl edit docker.service
```
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd

```console
sudo systemctl daemon-reload
sudo nano /etc/docker/daemon.json
```
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://127.0.0.1:2375"],
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "3"}
}

```console
sudo systemctl restart docker.service
```


# Docker install on linux
Depuis l'interface de dooker aller dans :
 - settings -> expose deamon
 - apply & restart
## Using a newer stack version

Tous les parametres de docker sont dans le [`.env`](/.env) il faut le modifier celon votre config notamment a variable referentials_files
Céer le fichier data

## airflow

```console
sudo chown 1000:1000 airflow_logs
docker-compose up airflow-init
```

### Airflow configuration

Il faut aller charger les variables du dags qui sont dans le docssier sources [config_airflow](/config_airflow/variables.json) et le charger dans Airflow  dans Admin -> [variables](http://localhost:8585/variable/list/).


### airflow dags

Le changement des dags ce fait tout seul depuis la lecture des fichiers en interne

Si on veut rebuild airflow il faut :

```console
docker-compose stop airflow-webserver airflow-scheduler airflow-worker; docker-compose up airflow-init;  docker-compose up -d airflow-webserver airflow-scheduler airflow-worker
```

## AIRBYTE
### Exporter les configurations

Aller dans Settings -> Configration -> Exporter

### Importer les configurations

Déplacer le fichier de configuartions et lancer la commande curl.

```console
curl -H "Content-Type: application/x-gzip" -X POST localhost:8000/api/v1/deployment/import --data-binary @/home/romain/Desktop/iiidata_docker/airbyte_config/airbyte.gz
```
