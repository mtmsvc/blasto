import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from blasto.utils import capitalize_name

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """<!doctype html>
<html>
  <head><title>BLASTO</title></head>
  <body><h1>Салам, БРАТИШШШКА!</h1></body>
</html>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/hello/{name}")
def hello(name: str) -> dict[str, str]:
    name = capitalize_name(name)
    return {"message": f"Hello, {name}!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
