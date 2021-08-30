#!/bin/bash

echo "Updating the system"
sudo apt update
echo "Upgrading the system"
sudo apt upgrade -y
echo "Installing prerequisites"
sudo apt install -y postgresql python3 python3-dev python3-pip
echo "Installing requirements"
pip3 install -r requirements.txt
echo "Setting postgres password to 'postgres'"
sudo -u postgres psql -c "alter user postgres with password 'postgres';"
echo "Creating database 'sensor_gateway'"
sudo -u postgres psql -c "create database sensor_gateway;"
echo "Done"
