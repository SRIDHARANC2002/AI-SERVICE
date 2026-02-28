venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
http://localhost:8000/docs