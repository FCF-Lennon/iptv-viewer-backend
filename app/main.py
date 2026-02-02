from fastapi import FastAPI
from app.core.config import setting


app = FastAPI(
    title=setting.app_name,
    debug=setting.debug
    )

@app.get("/health")
def health_check ():
    return {"status":"ok"} 

