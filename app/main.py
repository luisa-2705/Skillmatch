
from fastapi import FastAPI

from app.database.connection import Base, engine
from app.modules.usuarios import models as usuarios_models
from app.modules.vacantes import models as vacantes_models

from app.modules.usuarios.routes import router as usuarios_router
from app.modules.vacantes.routes import router as vacantes_router

from app.modules.habilidades import models as habilidades_models
from app.modules.habilidades.routes import router as habilidades_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Skill Match API",
    description="API para la plataforma de inteligencia de talento Skill Match",
    version="1.0.0"
)

app.include_router(usuarios_router)
app.include_router(vacantes_router)
app.include_router(habilidades_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Skill Match funcionando"
    }
