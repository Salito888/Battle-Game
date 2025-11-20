## Api Batalla Naval
FastAPI app

### Requirements
* Python 3.12

### Run

Create and enable virtual enviroment
```bash
python3.12 -m venv .venv
source .venv/bin/activate    # Activate on Linux
.\.venv\Scripts\activate     # Activate on Windows
```

Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
Run FastAPI application
```bash
uvicorn app.main:app --port 8000 --reload
```


