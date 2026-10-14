from fastapi import APIRouter, Depends

from app.services.usuario_service import crear_usuario, obtener_usuarios
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioResponse
from app.database.connection import get_db

router = APIRouter(
    prefix= "/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=UsuarioResponse)
def registrar_usuario(
    usuario: UsuarioCreate,
    db = Depends(get_db)
):

    return crear_usuario(db, usuario)

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db = Depends(get_db)):
    return obtener_usuarios(db)