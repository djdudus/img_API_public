# Image API Project

This Django project provides a RESTful API that allows users to upload, view, and manage images. Users are categorized into different tiers, and their access to the features is determined based on their assigned tier.

## Prerequisites

- Docker & Docker Compose

## Setting Up the Project

1. **Clone the repository:**
   ```bash  
   git clone https://github.com/djdudus/img_API_public.git
   cd img_API_public
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory and adjust the values accordingly:
   ```makefile
   POSTGRES_DB=<your_database_name>
   POSTGRES_USER=<your_database_user>
   POSTGRES_PASSWORD=<your_database_password>
   ```
      #### Database Configuration Details
      When you set the PostgreSQL environment variables for the first time:
      - **`POSTGRES_DB`**: Sets the name of the default database. If not set, the default `postgres` database will be used.
      - **`POSTGRES_USER`** and **`POSTGRES_PASSWORD`**: Define the superuser's credentials. If these are not provided, the default is the superuser `postgres` with no password.

      **Note**: These environment variables are effective only upon the initial start of the PostgreSQL container. If the container is restarted with existing data, these variables will not alter the existing setup. If you wish to apply new values, you would need to reset the container data.
  
3. **Configuration Changes:**
   For production environments, ensure you:
   - Update `ALLOWED_HOSTS` in `settings.py`. This should be set to the domain name of your deployment.
   - Match database settings in `settings.py` to your production database.

4. **Build and Run with Docker Compose:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

   The application will now be accessible on localhost, port 80.

## Using the Application

- **Django Admin Interface:** Can be accessed at `/admin/` where admins can manage users, account tiers, and other related tasks.

- **Browsable API from Django Rest Framework:** Provides an interface to interact with the API endpoints.

## Features
- **Login** `/login` To access all of the functions login to any user.
- **Image Upload:** `/upload` Users can upload images in PNG or JPG format.
- **Image Listing:** `/images` Users can list their uploaded images.
- **Account Tiers:** Users belong to plans (Basic, Premium, and Enterprise) that determine their access levels.
- **Thumbnail Generation:** Thumbnails are generated based on the user's plan.
- **Expiring Links:** `/generate-link` Enterprise plan users can generate expiring links to their images.

## Deploying to Production

- Update `settings.py`: Adjust `DEBUG` to `False` and update `ALLOWED_HOSTS` with your domain or IP address.
- Use a Production Database: Ensure your database settings in `settings.py` are set for your production database. Using the provided postgres image is okay for development but consider using a managed service for production.
- Secure your Environment Variables: Make sure your `.env` file or any other configuration is secure and not exposed to the public.
- Remember to always backup your database and other important data before making significant changes or updates to your application. It's also recommended to use a continuous integration and deployment (CI/CD) strategy to automate the testing and deployment processes.

## Further Configuration Details:

### Database Connection:
By default, the application connects to a PostgreSQL database using the settings provided in the `.env` file. To change this:
- Update your `.env` file with the correct database connection details.
- If switching to a different database, ensure you have the necessary drivers and libraries installed. For example, if switching to MySQL, you'll need the `mysqlclient` library.

### Allowed Hosts:
In Django, the `ALLOWED_HOSTS` setting defines which domains or IP addresses the application can serve. For security reasons, it's essential to set this correctly in a production environment.

```python
ALLOWED_HOSTS = ['myimageapi.com', 'www.myimageapi.com']
```

### Backup and Recovery:
- Regular Backups: Set up regular backups for your database. Tools like `pg_dump` for PostgreSQL can be used to create backup dumps.
- Backup Validation: Regularly test and validate your backups to ensure they can be restored.
- Disaster Recovery Plan: Have a plan in place detailing steps to take in case of data loss or system failures.
