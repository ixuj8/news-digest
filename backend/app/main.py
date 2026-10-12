from fastapi import FastAPI

app = FastAPI(title="News Digest API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
