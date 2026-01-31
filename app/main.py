from fastapi import FastAPI

app = FastAPI(title="IPTV Viewer Backend")

@app.get("/health")
def health_check ():
    return {"status":"ok"}
