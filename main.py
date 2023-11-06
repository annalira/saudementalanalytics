from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from uvicorn import run

from routers import columns
from routers import donut
from routers import line
from routers import maps
from routers import ranking
from routers import statics

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(columns.router)
app.include_router(donut.router)
app.include_router(line.router)
app.include_router(maps.router)
app.include_router(ranking.router)
app.include_router(statics.router)


@app.get("/", tags=["documentacao"])
async def index():
    return RedirectResponse("/docs")


if __name__ == '__main__':
    run("main:app", host="127.0.0.1", port=8000, reload=True)
