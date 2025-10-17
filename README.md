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

# 6. Start the app!
slate run
# OR use uvicorn directly:
python -m uvicorn main:app --app-dir src
# OR use FastAPI CLI:
fastapi dev src/main.py
fastapi run src/main.py
# Type `slate --help` to see all available CLI commands.
```

#### .env example:
```dotenv
# server
LOG_LEVEL=info

# auth
API_USERNAME=admin
API_TOKEN=secure_token
SECRET_KEY=secure_secret_key

# supabase 
DB_HOST=aws-0-us-east-1.pooler.supabase.com  
DB_NAME=postgres
DB_USER=postgres.project-ref
DB_PASSWORD=hash
```

#### SQL script located here [sql/001_schema.sql](works/sql/001_schema.sql)

---
