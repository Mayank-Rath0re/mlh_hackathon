# 🔗 TrimURL | MLH PE Hackathon

A lightning-fast, highly reliable URL shortener and analytics dashboard built for the MLH Product Engineering Hackathon. 

TrimURL isn't just about shortening links; it's built with a focus on **Site Reliability Engineering (SRE)** and **CI/CD** best practices. It features comprehensive test coverage, automated GitHub Actions workflows, branch protection, and real-time click tracking.

---

## 📑 Table of Contents
1. [Tech Stack](#-tech-stack)
2. [Prerequisites](#-prerequisites)
3. [Detailed Local Setup Guide](#-detailed-local-setup-guide)
4. [Using the Application](#-using-the-application)
5. [Running the Test Suite](#-running-the-test-suite)
6. [Hackathon Tracks Achieved](#-hackathon-tracks-achieved)
7. [Project Structure](#-project-structure)

---

## 🛠️ Tech Stack

* **Backend API:** Python 3.12+, Flask
* **Database:** PostgreSQL, Peewee ORM
* **Frontend:** Vanilla HTML, JavaScript, Tailwind CSS (via CDN)
* **Package Manager:** `uv` (Lightning fast Python dependency management)
* **DevOps / CI:** GitHub Actions, Pytest, Pytest-Cov

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:

1. **Python 3.12+**: [Download here](https://www.python.org/downloads/)
2. **PostgreSQL**: [Download here](https://www.postgresql.org/download/). Ensure the PostgreSQL server is actively running on your machine.
3. **uv Package Manager**: `uv` is required to manage dependencies instantly.
   * **macOS / Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
   * **Windows:** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

---

## 🚀 Detailed Local Setup Guide

Follow these exact steps to get the application running on your local machine in under 3 minutes.

### Step 1: Clone the Repository
Open your terminal and clone the repository to your local machine:
```bash
git clone <your-github-repo-url>
cd mlh-pe-hackathon
````

### Step 2: Install Dependencies

We use `uv` for dependency management. You do **not** need to manually create a virtual environment (`python -m venv`). `uv` handles this automatically.

```bash
uv sync
```

*This command reads the `pyproject.toml` file, creates a `.venv` folder, and installs all required packages (Flask, Peewee, Pytest, etc.) in milliseconds.*

### Step 3: Create the PostgreSQL Database

You need a local PostgreSQL database for the app to connect to. You can do this via pgAdmin or the `psql` command line tool:

**Using psql (Command Line):**

```bash
# Log into Postgres
psql -U postgres

# Create the database
CREATE DATABASE hackathon_db;

# Exit psql
\q
```

### Step 4: Configure Environment Variables

The application needs to know how to talk to your new database.

1.  Copy the example environment file:

<!-- end list -->

```bash
# Mac/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

2.  Open the `.env` file in your code editor and update it with your local PostgreSQL credentials. It should look like this:

<!-- end list -->

```ini
# Flask Environment
FLASK_APP=run.py
FLASK_ENV=development

# Database Configuration
DB_NAME=hackathon_db
DB_USER=postgres       # Change to your postgres username if different
DB_PASSWORD=password   # Change to your postgres password
DB_HOST=localhost
DB_PORT=5432
```

### Step 5: Seed the Database

Instead of manually creating tables, we have provided an automated seeding script. This script will:

1.  Connect to PostgreSQL.
2.  Create the `User`, `Url`, and `Event` tables.
3.  Read the provided MLH CSV files (`data/users.csv`, `data/urls.csv`, `data/events.csv`).
4.  Format the timestamps and insert the data.
5.  **Crucially:** Automatically sync the PostgreSQL internal sequences so you do not encounter `UniqueViolation` errors when creating new links.

Run the script:

```bash
uv run seed.py
```

*You should see a success message indicating the tables were created, data was loaded, and sequences were reset.*

### Step 6: Start the Server

Start the Flask development server:

```bash
uv run run.py
```

**🎉 Success\!** The app is now running. Open your browser and navigate to: **[http://localhost:5000](https://www.google.com/search?q=http://localhost:5000)**

-----

## 💻 Using the Application

1.  **Shorten a URL:** Go to the homepage (`/`), select a simulated user from the dropdown, paste a long URL, and click "Shorten".
2.  **Test the Redirect:** Click the newly generated short link. You will be seamlessly redirected to your original destination.
3.  **View Analytics:** Click the "📊 View Click Analytics" button below your generated link (or navigate to `/stats/<short_code>`). You will see a real-time dashboard displaying your captured IP address, User-Agent browser data, and total click counts.

-----

## 🧪 Running the Test Suite

This project includes a comprehensive test suite built with `pytest` and `pytest-flask`.

**Important:** The test suite uses an isolated, in-memory SQLite database (`:memory:`). This means you can safely run tests repeatedly without overwriting or deleting the data in your local PostgreSQL `hackathon_db`.

To run the tests and generate a coverage report:

```bash
uv run pytest --cov=app --cov-report=term-missing
```

*The `--cov-fail-under=50` flag is enforced in our CI pipeline to ensure quality standards.*

-----

## 🏆 Hackathon Tracks Achieved (Reliability Path)

This project was specifically engineered to conquer the **Reliability Path** of the MLH Product Engineering Hackathon.

### 🥉 Bronze Tier

  * **Automated Testing:** Implemented an isolated `pytest` suite ensuring core shortening and redirect logic functions flawlessly.
  * **CI Automation:** Configured a GitHub Actions workflow (`.github/workflows/ci.yml`) that spins up a PostgreSQL service container and runs tests on every push and pull request.
  * **Health Checks:** Added a `/health` endpoint to monitor application uptime.

### 🥈 Silver Tier

  * **Code Coverage:** Reached and enforced \>50% code coverage. The CI pipeline is explicitly configured to fail if coverage drops below this threshold.
  * **Protected Deploys:** Configured GitHub Branch Protection rules for the `main` branch, physically blocking PR merges unless all CI status checks (tests and coverage) pass.

### 🥇 Gold Tier (Chaos Engineering)

  * **Surviving Sabotage:** We successfully executed a chaos engineering drill. A fatal bug (breaking the shortening logic and destroying code coverage) was pushed to a feature branch.
  * **The Result:** The GitHub Action caught the failure, turned red, and the branch protection rules locked the merge, effectively saving the production `main` branch from an outage.

-----

## 📂 Project Structure

```text
.
├── .github/workflows/   # CI/CD pipelines (GitHub Actions)
├── app/
│   ├── models/          # Peewee ORM schema definitions
│   ├── routes/          # Flask Blueprints (API endpoints & UI rendering)
│   ├── templates/       # HTML/Tailwind UI files (index.html, stats.html)
│   ├── __init__.py      # Flask App factory
│   └── database.py      # Peewee database proxy configuration
├── data/                # Hackathon CSV seed files
├── tests/               # Pytest suite & SQLite conftest.py
├── .env.example         # Template for environment variables
├── pyproject.toml       # uv dependency management configuration
├── run.py               # Flask application entry point
└── seed.py              # Automated database setup and CSV ingestion script
```

-----

*Built with ❤️ for the MLH Product Engineering Hackathon.*

```
```