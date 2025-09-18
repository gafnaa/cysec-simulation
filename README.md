# bl1tz Store

## Description

This project is an e-commerce platform named "bl1tz Store" that offers premium electronics, fashion, and lifestyle products. It's built using Flask for the backend and Jinja2 for templating, with a MySQL database.

**This project is designed as a vulnerable web application for simulating and demonstrating Server-Side Template Injection (SSTI) and Remote Code Execution (RCE) attacks. It serves as an educational tool for understanding these vulnerabilities in a controlled environment.**

## Features

- User authentication (login, registration)
- Product listing and search functionality
- Admin dashboard for managing users, products, and uploads
- Customer support chat assistant
- Shopping cart functionality

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Python Library](/requirements.txt)

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/gafnaa/bl1tz-store.git
    cd bl1tz-store
    ```

2.  **Build and run the Docker containers:**
    ```bash
    docker compose up --build
    ```
    This command will:
    - Build the Docker images for the web application and the database.
    - Start the MySQL database container.
    - Start the Flask application container, which will wait for the database to be ready before starting.

## Running the Application

You should see output similar to this in your terminal:

```
app-1  | Database is ready!
app-1  |  * Serving Flask app 'app'
app-1  |  * Debug mode: off
app-1  | WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
app-1  |  * Running on all addresses (0.0.0.0)
app-1  |  * Running on http://127.0.0.1:5000
app-1  |  * Running on http://172.18.0.3:5000
app-1  | Press CTRL+C to quit
```

Once the containers are up and running, the application will be accessible at

```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```
