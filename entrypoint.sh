#!/bin/sh

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

#check for marker file
if [ ! -f "/tmp/init_data_done" ]; then
    echo "Initializing data"
    python manage.py init_data

    # Create a marker file to mark that init_data has been run
    touch /tmp/init_data_done
else
    echo "Data already initialized, skipping init_data"
fi
# Start Apache
echo "Starting Apache"
/usr/sbin/apache2ctl -D FOREGROUND
