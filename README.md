# slate_runner 🎬🐍
RESTful FastAPI for fixing it in post.

## Run service:
```bash
$ git clone https://github.com/johnshields/slate_runner.git
$ cd slate_runner
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python -m uvicorn main:app --app-dir src --host 127.0.0.1 --port 8049
```

#### .env example:
```dotenv
# server
API_HOST=0.0.0.0
API_PORT=8049
LOG_LEVEL=info

# auth
API_USERNAME=user
API_TOKEN=super-secret-token
SECRET_KEY=super-secret-key

# supabase pooler
DB_HOST=localhost
DB_PORT=5432
DB_NAME=slate_runner
DB_USER=user.hash
DB_PASSWORD=password
DB_SSLMODE=require
```

#### SQL script located here [sql/schema.sql](works/sql/schema.sql)

---
