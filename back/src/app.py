from fastapi import FastAPI

from src import database, models
from src.routers import ponto

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="API de Ponto 🕒")

app.include_router(ponto.router)


@app.get("/")
async def root():
    return {"message": "API de Ponto 🕒"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
