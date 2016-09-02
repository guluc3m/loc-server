# loc-server

## Installation

Use `virtualenv`:

```
virtualenv -p python3 venv && . venv/bin/activate

pip install -r requirements.txt
```

## Usage

First enable the virtualenv:

```
. venv/bin/activate
```

Perform database migrations:

```
FLASK_APP=runlocal.py flask db upgrade
```

Run local server:

```
FLASK_APP=runlocal.py flask run
```
