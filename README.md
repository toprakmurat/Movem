# Movem

A Flask web application for managing movies and actors database.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Movem
   ```

## Configuration

1. **Create a `.env` file** in the root directory with your database configuration:
   ```bash
   # Flask Configuration
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=<secret_key>

   # PostgreSQL Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=movem
   DB_USER=<username>
   DB_PASSWORD=<password>

   # Optional: Full DATABASE_URL (overrides individual DB_* variables if set)
   # DATABASE_URL=postgresql://username:password@localhost:5432/movem

   # Database Connection Pool Settings
   DB_MIN_CONNECTIONS=1
   DB_MAX_CONNECTIONS=20
   ```

2. **Environment Variables:**
   - `DB_HOST`: PostgreSQL host
   - `DB_PORT`: PostgreSQL port
   - `DB_NAME`: Database name
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password
   - `SECRET_KEY`: Flask secret key for sessions
   - `FLASK_ENV`: Environment (development/production/testing)

## Running the Application

### Prerequisites

Before you begin, ensure you have the following installed on your system:

* Docker
* Docker Compose

### Running the Application

1. **Build and start the services:**  
Run this command from the root directory (where your `docker-compose.yml` is):

```bash
docker-compose up --build
```

- `--build` tells Docker Compose to build the image from your Dockerfile.  
- You can add the `-d` flag (`docker-compose up --build -d`) to run the containers in detached (background) mode.

2. **Access the application:**  
The application will be available at: [http://127.0.0.1:5050](http://127.0.0.1:5050)

3. **Stop the services:**  

```bash
docker compose down
```

> This stops and removes the containers, but volumes remain intact.

You can also use:

```bash
docker compose stop    # Stop containers without removing
docker compose start   # Start stopped containers
```

### Testing the Application

1. **Check running containers:**

```bash
docker compose ps
```

It should show 2 services named `movem-flask-app-1` and `movem-postgres-1`.

2. **Connect to PostgreSQL while containers are running:**

```bash
docker exec -it movem-postgres-1 psql -U <DB_USER> -d <DB_NAME>
```

> Replace `<DB_USER>` and `<DB_NAME>` with the actual values from your `.env` file.  
> Once inside, you can use normal PostgreSQL commands like `\l` to list databases or `\dt` to list tables.
