#!/bin/bash

# Quick update script - run after pushing changes to GitHub
set -e

APP_DIR="/var/www/sitanetmerchant"

cd $APP_DIR
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
chown -R www-data:www-data $APP_DIR
systemctl restart sitanetmerchant

echo "Update complete! Check: systemctl status sitanetmerchant"
