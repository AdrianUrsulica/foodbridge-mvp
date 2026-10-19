# FoodBridge MVP

FoodBridge is a web application developed as part of the SWE6301 Agile Programming module.

The purpose of FoodBridge is to connect supermarkets, restaurants and cafés that have surplus food with charities that can collect and redistribute it.

The project is being developed using Scrum over multiple sprints.

## Technology

- Python
- Django 6.1.2
- SQLite (development database)
- Git and GitHub
- Jira for Scrum project management

## Sprint 1

The goal of Sprint 1 is to establish the project foundation and implement the User Accounts & Authentication functionality.

Sprint 1 includes:

- User Registration
- User Login
- Role-Based Access
- User Logout
- Authentication Testing & Acceptance Tests
- Project Setup & Integration

## Initial Project Setup

After cloning the repository, open a terminal in the project folder.

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install project dependencies

```powershell
pip install -r requirements.txt
```

### 4. Apply database migrations

```powershell
python manage.py migrate
```

### 5. Start the development server

```powershell
python manage.py runserver
```

Open the application at:

`http://127.0.0.1:8000/`

## Git Workflow

Do not develop directly on the `main` branch.

Before starting work:

1. Make sure your local `main` branch is up to date.
2. Create a separate branch for your Jira task.
3. Make changes only on your task branch.
4. Commit changes with a clear message including the Jira issue key.
5. Push the branch to GitHub.
6. Create a Pull Request into `main`.
7. Review and merge the Pull Request when the work is ready.

Example branch names:

```text
FB-2-user-registration
FB-3-user-login
FB-4-role-based-access
FB-5-user-logout
FB-7-authentication-testing
```

## Important

Do not commit local or sensitive files such as:

- `.venv/`
- `db.sqlite3`
- `.env`
- `__pycache__/`

These files are excluded through `.gitignore`.

If new Python packages are added to the project, update `requirements.txt` so that the rest of the team can install the same dependencies.

## Team Collaboration

All team members work from the same FoodBridge repository but use separate branches for their assigned Jira tasks.

Changes are integrated into `main` through Pull Requests to reduce conflicts and keep the project history clear.