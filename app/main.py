from fastapi import FastAPI
from app.core.config import setting
from app.api.routes.movies import router as movies_router
from app.api.routes.series import router as series_router


app = FastAPI(
    title=setting.app_name,
    debug=setting.debug
    )

app.include_router(movies_router)
app.include_router(series_router)

@app.get("/health")
def health_check ():
    return {"status":"ok"} 

