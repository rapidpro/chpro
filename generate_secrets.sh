#!/bin/bash

read_password () {
    read -s CHPRO_$1
    echo

    echo "$1"
    secret_name=CHPRO_$1
    echo "${!secret_name}"

    if [ -z "${!secret_name}" ]; then
      echo "Password cannot be left empty. Exiting."
      exit 1
    else
      { # try
      echo "Storing password..."
      echo -n "docker secret id: "
      echo "${!secret_name}" | docker secret create ${secret_name} -
      } || { # catch
      echo "Secret already exists. Edit it manually."
      exit 1
      }
    fi
}

echo -n "Enter the root password for the MySQL dabatase and press [ENTER]: "
read_password MYSQL_ROOT_PASSWORD
#echo
#echo -n "Enter the database name for the application and press [ENTER]: "
#read_password MYSQL_DATABASE
#echo
#echo -n "Enter the database user for the application and press [ENTER]: "
#read_password MYSQL_USER
echo
echo -n "Enter the database password for the application and press [ENTER]: "
read_password MYSQL_PASSWORD

