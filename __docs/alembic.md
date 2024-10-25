## Getting started for Database migrations with Alembic

1. Initialize the database migrations setup: `alembic init migrations`

2. Go to `alembic.ini`, and change the `[alembic]` item at line 3 to `[devdb]`

3. Go to `migrations/env.py` folder

```python
import os # new
from logging.config import fileConfig

from alembic import context
from dotenv import find_dotenv, load_dotenv # new
from sqlalchemy import engine_from_config, pool

from backend.db_models import Base # new

_ = load_dotenv(find_dotenv()) # new

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_section_option("devdb", "sqlalchemy.url", os.getenv("DATABASE_URL")) # new

# add your model's MetaData object here
target_metadata = Base.metadata

....
```

4. `alembic -n devdb revision --autogenerate`

5. `alembic -n devdb upgrade head`