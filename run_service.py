import os
import uvicorn

os.environ["SQL_HOST"] = r"localhost"
os.environ["SQL_USER"] = r"root"
os.environ["SQL_PASSWORD"] = r"root"
os.environ["DAYS_FOR_DELETION"] = r"7"

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5002, log_level="info", app_dir='app')
