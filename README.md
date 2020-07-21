# SIMPLE

If you'd like to participate or just stay in the loop as this project progresses, please request to join this discussion list:
https://groups.google.com/forum/#!forum/simple-archive

To see more details about what we've discussed so far, check out the running notes on the project: https://docs.google.com/document/d/1zDayF4ERMjj22QI3RaUZeTeb6nIVl3c2KDNw5WLLUqE/edit

## Getting Started

If you'd like to set up your own copy of the SIMPLE database, here's what we recommend:

1. Clone or download a copy of this repo somewhere locally

2. Set up an environment for the python code. 
A conda environment file exists for convenience.

3. Install the AstrodbKit2 package:

```bash
pip install git+https://github.com/dr-rodriguez/AstrodbKit2
```

5. Create the database. If you already have a binary DB file (eg, with SQLite), skip to the next step. 

```python
from astrodbkit2.astrodb import create_database
from simple.schema import *

connection_string = 'sqlite:///SIMPLE.db'  # SQLite
create_database(connection_string)
```

6. Connect to your existing database.

```python
from astrodbkit2.astrodb import Database

connection_string = 'sqlite:///SIMPLE.db'  # SQLite
db = Database(connection_string)
```

7. Load database contents from repo, if needed.

```python
db.load_database('data')
```
