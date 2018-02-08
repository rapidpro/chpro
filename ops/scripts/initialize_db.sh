docker exec -it `docker ps -f name=production_chpro.1 -q` fabmanager create-admin --app superset
docker exec -it `docker ps -f name=production_chpro.1 -q` superset db upgrade
docker exec -it `docker ps -f name=production_chpro.1 -q` superset init
