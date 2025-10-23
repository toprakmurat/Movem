# Movem

A Flask web application for managing movies and actors database.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Movem
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
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

Before running the application, ensure you have:
- A PostgreSQL service running in the background
- A database user configured with appropriate permissions

### Database Setup

1. **Create database user and database:**
   ```bash
   # Connect to PostgreSQL as superuser
   psql postgres
   ```

2. **In the PostgreSQL prompt, execute:**
   ```sql
   CREATE USER movem_user WITH PASSWORD 'your_password';
   CREATE DATABASE movem OWNER movem_user;
   GRANT ALL PRIVILEGES ON DATABASE movem TO movem_user;
   \q
   ```

### Starting the Application

1. **Activate your virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access the application:**
   
   The application will be available at `http://localhost:5000`
