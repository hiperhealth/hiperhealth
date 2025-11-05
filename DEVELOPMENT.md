# Contributor Guide

First off, thank you for considering contributing to `sdx`! We welcome all
contributions, from bug reports to new features and documentation improvements.
This guide provides everything you need to get your development environment set
up and start contributing.

Following these guidelines helps to communicate that you respect the time of the
developers managing and developing this open source project. In return, they
should reciprocate that respect in addressing your issue or assessing patches
and features.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started: Local Setup](#1-getting-started-local-setup)
- [Development Workflow](#2-development-workflow)
  - [Running the Applications](#running-the-applications)
  - [Database Migrations](#database-migrations)
  - [Code Style & Linting](#code-style--linting)
  - [Running Tests](#running-tests)
- [Architectural Overview](#3-architectural-overview)
- [Submitting Changes](#4-submitting-changes)

## Code of Conduct

This project and everyone participating in it is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to
uphold this code.

---

## 1. Getting Started: Local Setup

This project uses **Poetry** to manage dependencies and **makim** to streamline
development tasks.

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation) installed on your
  system.

### Installation

1.  **Fork & Clone the Repository:** Start by forking the repository on GitHub,
    then clone your fork locally:

    ```bash
    git clone git@github.com:<your-username>/sdx.git
    cd sdx
    ```

2.  **Install Dependencies:** This command creates a virtual environment and
    installs all packages from the `poetry.lock` file.

    ```bash
    poetry install
    ```

3.  **Set Up the Database:** Our `makim` task runner simplifies database setup.
    This command runs Alembic to create the `db.sqlite` file and applies all
    migrations.

    ```bash
    makim db.setup
    ```

4.  **(Optional) Set Up API Keys:** Certain tests and features that interact
    with external services (e.g., OpenAI) require API keys. Create a `.env` file
    at `sdx/.envs/.env` and add your keys there.
    ```dotenv
    # In .envs/.env
    OPENAI_API_KEY="your-key-here"
    ```

---

## 2. Development Workflow

All common development tasks are managed via `makim` commands defined in
`.makim.yaml`.

### Running the Applications

- **To run the Research Web App:**

  ```bash
  makim research.app
  ```

  The app will be available at `http://127.0.0.1:8000`.

- **To run the Research CLI:**
  ```bash
  makim research.cli
  ```

### Database Migrations

The database schema is managed with Alembic. The schema's source of truth is the
set of Pydantic models in `src/sdx/schema/`, which are used to auto-generate the
SQLAlchemy ORM models.

If you modify a Pydantic schema that requires a database change:

1.  **Regenerate the SQLAlchemy Models:**

    ```bash
    makim models.sqla
    ```

2.  **Generate a New Migration Script:** Provide a descriptive message for the
    change.

    ```bash
    makim db.revision -m "A short description of the schema change"
    ```

3.  **Apply the Migration to Your Local Database:**
    ```bash
    makim db.setup
    ```

### Code Style & Linting

We enforce code quality and a consistent style using `pre-commit` hooks,
configured in `.pre-commit-config.yaml`.

- **Install Git Hooks:**

  ```bash
  poetry run pre-commit install
  ```

  The hooks will now run automatically on every commit.

- **Run Hooks Manually:** To run the checks on all files at any time:
  ```bash
  makim test.pre-commit
  ```

### Running Tests

Our test suite uses `pytest`.

- **Run All Tests:**

  ```bash
  makim test.run
  ```

- **Run Tests with Coverage Report:**
  ```bash
  makim test.coverage
  ```

---

## 3. Architectural Overview

The `sdx` library follows a "schema-first" approach for its database models.

1.  **Pydantic Schemas (`src/sdx/schema/`)**: These are the primary source of
    truth. They define the data structures and validation rules for our
    application.
2.  **SQLAlchemy Models (`src/sdx/models/sqla/`)**: These ORM models are
    **auto-generated** from the Pydantic schemas using the
    `scripts/gen_models/gen_sqla.py` script (`makim models.sqla`). **Do not edit
    these files manually.**
3.  **Alembic Migrations (`migrations/`)**: Alembic uses the generated
    SQLAlchemy models to automatically create database migration scripts.

This ensures our application's data layer and database schema are always
perfectly synchronized.

---

## 4. Submitting Changes

1.  Create a new branch for your feature or bugfix.
2.  Make your changes, ensuring you add tests for any new functionality.
3.  Ensure all tests pass and the linter is happy.
4.  Push your branch to your fork and open a Pull Request against the `main`
    branch of the upstream repository.
5.  In your PR description, clearly explain the problem and your solution.
    Include the relevant issue number if applicable.
