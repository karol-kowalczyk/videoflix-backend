# Videoflix Backend

Backend for the Videoflix Project

Videoflix is a video-on-demand platform for end users. The frontend can be found here: [Videoflix Frontend](https://github.com/karol-kowalczyk/video_flix_frontend)

## Features

- Registration with email validation and login.
- Password reset functionality.
- Overview of a list of all videos.

## Prerequisites

- Python (version 3.x)
- Django (version and additional packages listed in `requirements.txt`)

All required dependencies can be installed via `requirements.txt` (see step 3).

## Installation on a Linux System

### 1. Clone the project

```bash
cd to_your_project_directory
git clone git@github.com:karol-kowalczyk/videoflix-backend.git
cd videoflix-backend
```
### 2. Create a virtual environment
Create and activate a virtual Python environment:
```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the Django project
Migrate the database and start the server:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
The project will run, depending on your configuration, at http://127.0.0.1:8000.

###  5. Create a superuser (admin)
You can create a superuser directly via the terminal with the following command:
```bash
python manage.py createsuperuser
```

### 6. Video upload via management command or API view
To upload videos using a management command:
```bash
python manage.py create_video_list
```
Before using this command, you must adjust the video list with the appropriate filenames. Alternatively, the videos can be provided upon request. The folder containing the videos must be specified in the .env file under VIDEO_FOLDER.

To upload videos via the API view:
http://127.0.0.1:8000/api/video/

The thumbnail filenames must follow this format:
ANY-NAME_ALLOWED-CATEGORY.jpg or .png

Allowed categories are listed in the .env file under ALLOWED_CATEGORIES. The category in the filename determines the video category, which is extracted during the upload process.


## Configuration
In the settings.py file, several important settings have been configured to run the project locally:
```bash
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'videoflix_app',
    'debug_toolbar',
    'django_rq',
    'import_export',
    'users',
]
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```
These settings enable permissions and authentication.

## Usage
Once the server is running, you can use the API to interact with the Videoflix frontend. Here are some useful commands:

Migrate the database:
```bash
python manage.py makemigrations
python manage.py migrate
Start the development server:

python manage.py runserver
Deployment
```
License
This project was created as part of a learning project and is provided without a specific license.
