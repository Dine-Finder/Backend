## Dine Finder Project Backend Setup Guide

https://dinefinder.site/

### Introduction
Welcome to the Dine Finder project! This application helps users discover and explore a wide variety of restaurants based on their preferences and location. The backend setup guide will walk you through the necessary steps to get your development environment up and running smoothly.

### Video Tutorial
For a comprehensive step-by-step guide on setting up the Dine Finder frontend, watch the video tutorial below:

<p align="center">
  <a href="https://youtu.be/I2ugolvJmPA">
    <img src="https://connectthedotspr.com/wp-content/uploads/2018/06/watch-video-icon.jpg" alt="Watch the video">
  </a>
</p>

### Key Features
- **✨ User-friendly interface** for easy navigation and restaurant discovery
- **🌟 Personalized recommendations** based on user preferences and location
- **📸 Detailed restaurant information**, including menus, photos, and reviews
- **🍽️ Reservation and ordering capabilities** for a seamless dining experience

### Overview
This guide provides detailed instructions for setting up the environment and deploying the Dine Finder application across Windows, macOS, and Linux operating systems. By following these steps, you'll have a solid foundation to start building and testing your application.

### Prerequisites
Before proceeding with the setup, ensure that you have the following installed on your system:

- **Python 3.x**
- pip (Python package installer)
- virtualenv (optional but recommended)

### Environment Setup
To begin, navigate to your project directory where the `requirements.txt` file is located.

#### Windows
Open PowerShell and execute the following commands:

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### macOS and Linux
Open Terminal and run:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This will create a virtual environment, activate it, and install all the necessary dependencies specified in the `requirements.txt` file.

### Configuration File Setup
Create a `.env` file in your project directory to store sensitive keys and configurations. Use your preferred text editor:

#### Windows
```bash
notepad .env
```

#### macOS and Linux
```bash
nano .env
```

#### Obtain Your Google Maps API Key
To display restaurant locations on a map, you'll need to obtain a Google Maps API key. Follow these steps:

1. Visit the [Google Maps Platform website](https://developers.google.com/maps).
2. Sign in to your Google account or create a new one if you don't have one.
3. Create a new project and enable the Google Maps JavaScript API.
4. Generate an API key and copy it for later use.

#### Add the Following to Your `.env` File:
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

Replace `YOUR_SECRET_KEY`, `USER`, `PASSWORD`, `YOUR_GOOGLE_MAPS_API_KEY`, `EMAIL`, `EMAIL_APP_PASSWORD`, and `YOUR_SECURITY_SALT` with your actual values.

### Set Flask Environment
Configure the Flask environment variable according to your setup requirements.

#### For Production:
```bash
export FLASK_ENVIRONMENT=production
```

#### For Debugging:
```bash
export FLASK_ENVIRONMENT=development
```

#### To Verify the Current Flask Environment Setting, Run:
```bash
echo $FLASK_ENVIRONMENT
```

### Running the Application
With your environment and configuration files set up, you can now run the application:

```bash
flask run
```

This command will start the Flask development server, and you should be able to access the Dine Finder application in your web browser at `http://localhost:5000`.

### Docker Setup
We have Docker images available to streamline the setup process. You can pull the images from Docker Hub using the following commands:

#### Backend Flask Application:
```bash
docker pull musaddique333/backend-flaskapp
```

#### Nginx for Backend:
```bash
docker pull musaddique333/backend-nginx
```

For more details, visit the Docker repositories:
- [Backend Flask Application](https://hub.docker.com/repository/docker/musaddique333/backend-flaskapp/general)
- [Backend Nginx](https://hub.docker.com/repository/docker/musaddique333/backend-nginx/general)


### Project Structure
The Dine Finder project follows a modular structure to keep the codebase organized and maintainable. Here's a breakdown of the main directories and files:

```
Backend/
├── .github/
│   ├── workflows/
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

### Contributing
We welcome contributions to the Dine Finder project! To contribute, please follow these steps:

1. **Fork the repository** to your own GitHub account.
2. **Clone the forked repository** to your local machine.
3. Create a new branch with a descriptive name for your feature or bugfix.
4. Make your changes and commit them with clear and concise commit messages.
5. Push your changes to your forked repository.
6. Create a pull request to the main repository's `main` branch with a description of your changes.

For more detailed instructions, please refer to our [Contributing Guidelines](CONTRIBUTING.md).

### Conclusion
After completing these steps, your Dine Finder backend should be fully operational. You can now proceed with building the frontend and integrating it with the backend to create a complete and functional application.

For further configurations, troubleshooting, or if you have any questions, please consult the official Flask documentation or reach out to the project maintainers.

Happy coding and enjoy exploring the world of restaurants with Dine Finder!