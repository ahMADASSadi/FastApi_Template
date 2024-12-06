
# FastAPI Project Template

## Overview

This is a FastAPI project template that provides a customizable migration manager. It is designed to help developers quickly set up a FastAPI application with a robust database migration system powered by **Alembic**. The project uses the **Poetry** package manager for dependency management and virtual environment handling.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.12 or higher
- pip (Python package installer)

## Installation

### Step 1: Install Poetry

If you don't already have Poetry installed, you can install it using pip:

```bash
pip install poetry
```

### Step 2: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/ahMADASSadi/FastApi_Template.git
```

### Step 3: Install Dependencies and Activate the Environment

Navigate to the project directory and run the following commands:

```bash
poetry env use python3.12
poetry install
poetry shell
```

## Usage

This project is designed for ease of use. With just a few commands, you can make migrations, apply migrations, and run the server. Follow these steps:

> **Note**: Ensure you have set up and configured the database before proceeding to avoid issues.

Navigate to the root of the project (the directory containing the `app` folder) to ensure the commands work correctly.

### Create Migrations

```bash
python -m app.main makemigrations
```

### Apply Migrations

```bash
python -m app.main migrate
```

### Run the Server

```bash
python -m app.main
```

## Contributing

That's it! 🎉 

Contributions to improve and enhance this project are highly welcome! Feel free to fork the repository and submit a pull request. 😊