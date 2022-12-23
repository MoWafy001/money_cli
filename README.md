# Money CLI
A command line interface I made to manage money. It's a work in progress, but it's functional. I'm not sure if it's useful to anyone else, but I thought I'd share it anyway.

## Installation
- [Money CLI](#money-cli)
  - [Installation](#installation)
    - [Clone the repository](#clone-the-repository)
    - [Create a virtual environment](#create-a-virtual-environment)
    - [Install the requirements](#install-the-requirements)
    - [Create a `.env` file](#create-a-env-file)
    - [Create a user](#create-a-user)
    - [Run](#run)

### Clone the repository
```bash
git clone https://github.com/MoWafy001/money_cli.git

# Then cd into the directory
cd money_cli
```

### Create a virtual environment
```bash
python3 -m venv env

# Activate the virtual environment
source env/bin/activate
```
The script (`money`) expects the virtual environment to be named `env`. If you want to change the name, you'll have to change the script.

### Install the requirements
```bash
pip install -r requirements.txt
```

### Create a `.env` file
```bash
cp .env.example .env
```
Then edit the file to your liking.

### Create a user
```bash
python3 create_user.py <username>
```

### Run
```bash
./money
```