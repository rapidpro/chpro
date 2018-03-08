#!/usr/bin/env bash
if [  $# -le 1 ]
then
    echo 'Ussage: load_db_dump.sh <db_name> <sql_file>'
    exit 1
fi

echo "CREATE DATABASE $1" | docker exec -i chpro-db bash -c 'mysql --user=root --password="$(cat /run/secrets/MYSQL_ROOT_PASSWORD)"'
echo "GRANT ALL PRIVILEGES ON $1.* TO \`superset\`@\`%\`;" | docker exec -i chpro-db bash -c 'mysql --user=root --password="$(cat /run/secrets/MYSQL_ROOT_PASSWORD)"'
echo 'FLUSH PRIVILEGES;' | docker exec -i chpro-db bash -c 'mysql --user=root --password="$(cat /run/secrets/MYSQL_ROOT_PASSWORD)"'

# Concatenating the command strings for proper variable expansion
db_name=$1
base_script='mysql --user=superset --password="$(cat /run/secrets/MYSQL_PASSWORD)" -D '
final=$(echo $base_script $db_name)
cat $2 | docker exec -i chpro-db bash -c "${final}"
