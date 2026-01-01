# Gutenberg Books REST API

A Flask REST API for querying Project Gutenberg books from a PostgreSQL database.

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd /home/tank/Desktop/API3
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**

   **Create the database:**
   ```bash
   createdb gutendex
   ```

   **Restore from dump file:**
   ```bash
   psql gutendex < gutendex.dump
   ```

5. **Create and configure `.env` file:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=gutendex
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

6. **Run the Flask application:**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

## Live API Deployment

The API is deployed and publicly accessible here:

🔗 https://gutenberg-api-vercel.onrender.com/

### Example Endpoints

- Root: https://gutenberg-api-vercel.onrender.com/
- Books API: https://gutenberg-api-vercel.onrender.com/api/books
