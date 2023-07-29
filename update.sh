#!/bin/bash

echo "Pull git repo"
git pull

echo "Rebuild container"
sudo docker-compose down && sudo docker-compose build && sudo docker-compose up -d
