# slate_runner 🎬🐍
RESTful FastAPI for fixing it in post.

## Run service:
```bash
# 1. Get Python 3.13+ first (https://www.python.org/downloads/)

# 2. Clone the project
git clone https://github.com/johnshields/slate_runner.git
cd slate_runner

# 3. Create a virtual environment
python -m venv .venv

# 4. Activate the venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows PowerShell

# 5. Install everything you need
pip install -e ".[dev]"

# 6. Run the API!
slate run

# Type `slate --help` to see all available commands.

# Alt
pip install -r requirements.txt
python -m uvicorn main:app --app-dir src --host 127.0.0.1 --port 8049
```

#### .env example:
```dotenv
# server
API_HOST=0.0.0.0
API_PORT=8049
LOG_LEVEL=info
ENVIRONMENT=development
SERVICE=slate_runner_api

# auth
API_USERNAME=user
API_TOKEN=token
SECRET_KEY=secret

# supabase pooler
DB_HOST=localhost
DB_PORT=5432
DB_NAME=slate_db
DB_USER=user.hash
DB_PASSWORD=password
DB_SSLMODE=require
```

#### SQL script located here [sql/001_schema.sql](works/sql/001_schema.sql)

---
