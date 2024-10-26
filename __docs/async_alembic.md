## Getting started for Database migrations with Alembic

1. Initialize Alembic in the project. Use the -t async flag for asynchronous support.: `alembic init -t async migrations`

2. Go to `alembic.ini`, and change the `[alembic]` item at line 3 to `[devdb]`



3. Go to `migrations/env.py` folder

```python
import asyncio
import os
from logging.config import fileConfig

from alembic import context
from dotenv import find_dotenv, load_dotenv  # new
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from backend.db_models import Base  # new

_ = load_dotenv(find_dotenv())  # new

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_section_option("devdb", "sqlalchemy.url", os.getenv("DATABASE_URL"))  # new

target_metadata = Base.metadata # new
....
```

4. `alembic -n devdb revision --autogenerate`

5. `alembic -n devdb upgrade head`