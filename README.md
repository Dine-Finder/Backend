# Dine Finder Project Backend Setup Guide

## Video Tutorial
Watch the video tutorial for a step-by-step guide on setting up the Dine Finder frontend:

[![Dine Finder Frontend Setup](https://drive.google.com/file/d/1l49K96oNVxvUzkMSykx0kGD8RNpArLJK/view?usp=sharing)](https://drive.google.com/file/d/1qdo-ErIzOY6r3ZROa0RJa3LEEXDXZTXb/view?usp=sharing)


## Overview
This guide provides detailed instructions for setting up the environment and deploying the Dine Finder application on Windows, macOS, and Linux operating systems.

## Environment Setup
First, navigate to your project directory where the `requirements.txt` file is located.

### Windows
Open Powershell run:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### macOS and Linux
Open Terminal and run:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration File Setup
Create a `.env` file in your project directory to store sensitive keys and configurations. Use your preferred text editor, for example:

### Windows
```bash
notepad .env
```

### macOS and Linux
```bash
nano .env
```

### Get your Google maps api key here
```plaintext
https://developers.google.com/maps
```

### Add the following to your `.env` file:
```plaintext
SECRET_KEY=YOUR_SECRET_KEY
JWT_SECRET_KEY=YOUR_SECRET_KEY

DEV_DATABASE_URI=mysql+pymysql://USER:PASSWORD@localhost/flaskapp
PROD_DATABASE_URI=mysql+pymysql://USER:PASSWORD@localhost/flaskapp

FLASK_ENVIRONMENT=Development
REACT_APP_GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=EMAIL
MAIL_PASSWORD=EMAIL_APP_PASSWORD
SECURITY_PASSWORD_SALT=YOUR_SECURITY_SALT
```

## Set Flask Environment
Configure the Flask environment variable according to your setup requirements.

### For production:
```bash
export FLASK_ENVIRONMENT=production
```

### For debugging:
```bash
export FLASK_ENVIRONMENT=development
```

### To verify the current Flask environment setting, run:
```bash
echo $FLASK_ENVIRONMENT
```

## Running the Application
Now that your environment and configuration files are set up, you can run the application.

```bash
flask run
```

## Conclusion
After following these steps, your Dine Finder application should be up and running. For further configurations and troubleshooting, consult the official Flask and Anaconda documentation.

## Project Structure

Below is the structure of the project detailing the directories and files contained within:

```
Backend/
├── .github/
│   ├── work/flows
│   │   ├── backend.yml
├── flaskapp/
│   ├── build/
│   ├── templates/
│   │   ├── reset_password.html
│   │   └── verify_email.html
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── restaurants.py
├── model/
│   ├── model.pkl.gz
├── .gitignore
├── .env
├── config.py
├── requirements.txt
├── Dockerfile-flask
├── Dockerfile-nginx
├── docker-compose.yml
├── nginx.conf
├── dinefinder.conf
├── README.md
├── LICENSE
└── app.py
```