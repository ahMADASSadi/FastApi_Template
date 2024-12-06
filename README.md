# FastAPI Project Template

## Overview

This is a FastAPI project template that provides a customizable migration manager. It is designed to help developers quickly set up a FastAPI application with a robust database migration system using Alembic. The project utilizes the **Poetry** package manager for dependency management and virtual environment handling.

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

Clone this repository to your local machine either using the github desktop or

```bash
git clone https://github.com/ahMADASSadi/FastApi_Template.git
```

### Step 3: Install the requirements from poetry.lock file and activate the environment

```bash
poetry env use python3.12

poetry install

poetry shell
```

## Usage

it's designed for ease of use so only with few command you can make migrations, migrate and run you server, below are the commands:

(first ensure you have the database setup and installed so there are no prpblem to face with)

navigate to the root of the project that contains the app folder so the commands work just fine

### Make the migrations

```bash
python -m app.main makemigrations

```

### Migrate

```bash
python -m app.main migrate

```

### Run the server

```bash
python -m app.main
```

## **That's it !!!** 

i`d be happy of your contribion to improve and begreaten this project **:)**
