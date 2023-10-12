FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update -y && apt-get -y install apache2 libapache2-mod-wsgi-py3 && apt-get clean && apt-get autoremove

# Install Python dependencies
COPY requirements.txt $APP_HOME/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files to container
COPY . $APP_HOME/

# Set permissions for the app user
RUN groupadd -g 1000 app && useradd -u 1000 -g app -s /bin/sh app && chown -R app:app $APP_HOME

ENV APACHE_RUN_USER app
ENV APACHE_RUN_GROUP app

# Configure Apache
COPY mysite.conf /etc/apache2/sites-available/
RUN a2ensite mysite.conf && a2dissite 000-default.conf

# Expose Apache port
EXPOSE 80

# Start Apache in foreground
CMD ["./entrypoint.sh"]
