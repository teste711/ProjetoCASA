from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from . import storage
from .routers import auth, categorias, dispositivos, historico, midias, notificacoes, perfil

@asynccontextmanager
async def lifespan(_: FastAPI):
    storage.garantir_pasta()
    yield


app = FastAPI(lifespan=lifespan, title="C.A.S.A. API", version="2.0.0",
              description="Auth: Firebase Authentication (token Bearer). Dados: Cloud Firestore.")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
                   allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(HTTPException)
async def _http(_: Request, e: HTTPException):
    d = e.detail if isinstance(e.detail, dict) else {"codigo": "erro", "mensagem": str(e.detail)}
    return JSONResponse(status_code=e.status_code, content={**d, "detail": d["mensagem"]})


@app.exception_handler(RequestValidationError)
async def _val(_: Request, e: RequestValidationError):
    msg = e.errors()[0]["msg"].removeprefix("Value error, ") if e.errors() else "Dados inválidos."
    return JSONResponse(status_code=422, content={"codigo": "validacao", "mensagem": msg, "detail": msg})


for r in (auth.router, midias.router, perfil.router, categorias.router, dispositivos.router, historico.router, notificacoes.router):
    app.include_router(r)


@app.get("/saude", tags=["Sistema"])
def saude():
    return {"status": "ok"}
