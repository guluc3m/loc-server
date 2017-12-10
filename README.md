# loc-server

Implementation of the League of Code API backend.

## Installation

Use `virtualenv`:

```
virtualenv -p python3 venv && . venv/bin/activate

pip install -r requirements.txt
```

Depending on the database to use and the broker for asynchronous tasks (for
Celery), some other requirements may apply.


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


## Test data

For testing purposes, there is a command that can be used to fill the database
with sample data. **This should only be used in development or testing
environments**.

```
FLASK_APP=runlocal.py flask db upgrade
FLASK_APP=runlocal.py flask dbseed
```
