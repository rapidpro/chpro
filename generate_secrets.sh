#!/bin/bash

read_password () {
    read -s CHPRO_$1
    secret_varname=CHPRO_$1

    if [ -z "${!secret_varname}" ]; then
      echo "Password cannot be left empty. Exiting."
      exit 1
    else
      { # try
      echo "Storing password..."
      echo -n "docker secret id: "
      echo "${!secret_varname}" | docker secret create $1 -
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

