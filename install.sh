#!/bin/bash

# Variables
TARGET_DIR="/var/www/html/tmd-tvc"
LOG_FILE="/var/log/fetch_services.log"
DB_NAME="stream_service_monitor"
DB_USER="monitor_user"
DB_PASS="password"

# Detect the operating system
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Unsupported OS"
    exit 1
fi

# Update and install necessary packages based on the OS
if [ "$OS" == "ubuntu" ]; then
    sudo apt-get update
    sudo apt-get install -y apache2 libapache2-mod-php php php-mysql ffmpeg python3 python3-pip mysql-server
    sudo a2enmod cgi
    sudo systemctl enable apache2
    sudo systemctl start apache2

elif [ "$OS" == "rhel" ] || [ "$OS" == "centos" ]; then
    sudo yum update -y
    sudo yum install -y httpd mod_php php php-mysqlnd ffmpeg python3 python3-pip mariadb-server
    sudo systemctl enable mariadb
    sudo systemctl start mariadb
    sudo systemctl enable httpd
    sudo systemctl start httpd
    sudo yum install -y epel-release
    sudo yum install -y mod_fcgid
else
    echo "Unsupported OS"
    exit 1
fi

# Install psutil
sudo pip3 install psutil

# Create target directory
if [ ! -d "$TARGET_DIR" ]; then
  sudo mkdir -p "$TARGET_DIR"
fi

# Copy project files
sudo cp -r web/* "$TARGET_DIR/"
sudo cp -r cgi-bin "$TARGET_DIR/"

# Set permissions
sudo chown -R www-data:www-data "$TARGET_DIR"
sudo chmod -R 755 "$TARGET_DIR"

# Configure Apache for CGI and PHP
CGI_CONFIG="<IfModule alias_module>
    ScriptAlias /cgi-bin/ \"$TARGET_DIR/\"
</IfModule>

<Directory \"$TARGET_DIR\">
    AllowOverride None
    Options +ExecCGI
    AddHandler cgi-script .py .pl
    Require all granted
</Directory>

<IfModule mime_module>
    AddType application/x-httpd-php .php
</IfModule>"

if [ "$OS" == "ubuntu" ]; then
    echo "$CGI_CONFIG" | sudo tee /etc/apache2/conf-available/stream-service-monitor.conf
    sudo a2enconf stream-service-monitor
    sudo systemctl restart apache2
elif [ "$OS" == "rhel" ] || [ "$OS" == "centos" ]; then
    echo "$CGI_CONFIG" | sudo tee /etc/httpd/conf.d/stream-service-monitor.conf
    sudo systemctl restart httpd
fi

# Set up MySQL database
sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
sudo mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Create users table
sudo mysql -u "$DB_USER" -p"$DB_PASS" -D "$DB_NAME" -e "
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);"

# Make fetch_services.py executable
sudo chmod +x "$TARGET_DIR/cgi-bin/fetch_services.py"

echo "Installation completed. Open your web browser and navigate to http://<your-server-ip>/tmd-tvc/"
