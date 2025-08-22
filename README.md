# slate_runner 🎬🐍
RESTful FastAPI for fixing it in post.

#### Run service:
```bash
$ git clone https://github.com/johnshields/slate_runner.git
$ cd slate_runner
$ pip install -r requirements.txt
$ python -m uvicorn main:app --app-dir src --host 127.0.0.1 --port 8049
```

#### .env example:
```dotenv
# server
API_HOST=0.0.0.0
API_PORT=8049
LOG_LEVEL=info

# supabase pooler
DB_HOST=localhost
DB_PORT=5432
DB_NAME=slate_runner
DB_USER=user.hash
DB_PASSWORD=password
DB_SSLMODE=require
```

---
