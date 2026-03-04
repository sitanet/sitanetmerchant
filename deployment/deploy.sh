#!/bin/bash

# Sitanet Merchant Deployment Script
# Run this script on your Digital Ocean droplet as root

set -e

APP_NAME="sitanetmerchant"
APP_DIR="/var/www/$APP_NAME"
REPO_URL="https://github.com/sitanet/sitanetmerchant.git"
DOMAIN="sitanetmerchant.sitanetorbit.com"

echo "======================================"
echo "Sitanet Merchant Deployment Script"
echo "======================================"

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "Installing dependencies..."
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx git

# Create PostgreSQL database and user
echo "Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE $APP_NAME;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER ${APP_NAME}_user WITH PASSWORD 'CHANGE_THIS_PASSWORD';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "ALTER ROLE ${APP_NAME}_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE ${APP_NAME}_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE ${APP_NAME}_user SET timezone TO 'Africa/Lagos';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $APP_NAME TO ${APP_NAME}_user;"

# Create application directory
echo "Setting up application directory..."
mkdir -p $APP_DIR
mkdir -p /var/log/gunicorn
mkdir -p /run/gunicorn

# Clone or pull repository
if [ -d "$APP_DIR/.git" ]; then
    echo "Pulling latest changes..."
    cd $APP_DIR
    git pull origin main
else
    echo "Cloning repository..."
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Create virtual environment and install dependencies
echo "Setting up Python environment..."
python3 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file (if not exists)
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env file from template..."
    cp $APP_DIR/deployment/.env.production $APP_DIR/.env
    echo "IMPORTANT: Edit $APP_DIR/.env with your actual credentials!"
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Set ownership
chown -R www-data:www-data $APP_DIR
chown -R www-data:www-data /var/log/gunicorn
chown -R www-data:www-data /run/gunicorn

# Setup systemd service
echo "Setting up systemd service..."
cp $APP_DIR/deployment/sitanetmerchant.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sitanetmerchant
systemctl restart sitanetmerchant

# Setup Nginx
echo "Setting up Nginx..."
cp $APP_DIR/deployment/nginx.conf /etc/nginx/sites-available/sitanetmerchant
ln -sf /etc/nginx/sites-available/sitanetmerchant /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Setup SSL with Let's Encrypt
echo "Setting up SSL certificate..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@sitanetorbit.com --redirect

# Setup firewall
echo "Configuring firewall..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable

echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "IMPORTANT: Update $APP_DIR/.env with your actual credentials:"
echo "1. Generate a new SECRET_KEY"
echo "2. Set your database password"
echo "3. Add your API credentials"
echo ""
echo "Then restart the service:"
echo "  systemctl restart sitanetmerchant"
echo ""
echo "Check status:"
echo "  systemctl status sitanetmerchant"
echo "  journalctl -u sitanetmerchant -f"
echo ""
echo "Your site should be available at: https://$DOMAIN"
