## Docker install

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


## Using a newer stack version

Tous les parametres de docker sont dans le `.env` il faut le demander aux cretins (romain/kevin)
Pour les projets python, pour les builds il faut le fichier `github_key` encore à demander auw cretins.

```console
mkdir elasticsearch_data
sudo chown 1000:1000 elasticsearch_data
docker-compose build
docker-compose up
```

### Changements au niveaux des logs (ELK et rabbitmq)

Pour modifier le comportement des logs il y a [logstash](/logstash/pipeline/logstash.conf) et [rabbitmq](/rabbitmq/custom_definitions.json) et ne pas oublier de modifier les paramatres dans les applications.

Pour re-build l'application il faut ELK :

```console
 docker-compose stop logstash filebeat kibana elasticsearch; docker-compose build logstash filebeat kibana elasticsearch; docker-compose up -d logstash filebeat kibana elasticsearch
```

#### Rotation des logstash

Mise en place d'une capacitée maximum d'allocation de taille pour logstash, si on veux le modifier on est obliger d'aller dans la console de kibana, la [dev tools](http://iiidataserver.ddns.net:5601/app/dev_tools#/console)

```console
PUT _cluster/settings
{
  "transient": {
    "cluster.routing.allocation.disk.watermark.low": "30gb",
    "cluster.routing.allocation.disk.watermark.high": "10gb",
    "cluster.routing.allocation.disk.watermark.flood_stage": "1gb",
    "cluster.info.update.interval": "1m"
  }
}


## airflow

```console
sudo chown 1000:1000 airflow_logs
docker-compose up airflow-init
```

### airflow dags

Le changement des dags ce fait tout seul depuis la lecture des fichiers en interne mais il faut les telechargé depuis le git

```console
cd ~/Desktop/iiidata_docker
git pull
```

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
