from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.modules.usuarios.models import Usuario
from app.modules.vacantes.models import Vacante, VacanteHabilidad
from app.modules.vacantes.schemas import (
    VacanteCreate,
    VacanteResponse,
    VacanteHabilidadCreate,
    VacanteHabilidadResponse
)
from app.modules.habilidades.models import Habilidad

router = APIRouter(prefix="/vacantes", tags=["Vacantes"])


@router.post("/", response_model=VacanteResponse)
def crear_vacante(
    vacante: VacanteCreate,
    empleador_id: int,
    db:Session = Depends(get_db)
):
    empleador = db.query(Usuario).filter(
        Usuario.id == empleador_id
    ).first()

    if not empleador:
        raise HTTPException(
            status_code=404,
            detail="El usuario empleador no existe"
        )

    if empleador.tipo_usuario != "EMPLEADOR":
         raise HTTPException(
        status_code=403,
        detail="Solo los empleadores pueden publicar vacantes"
    )

    nueva_vacante = Vacante(
        **vacante.model_dump(),
        empleador_id = empleador_id
    )

    db.add(nueva_vacante)
    db.commit()
    db.refresh(nueva_vacante)

    return nueva_vacante

@router.get("/", response_model=list[VacanteResponse])
def listar_vacantes(db: Session = Depends(get_db)):
    return db.query(Vacante).order_by(
        Vacante.fecha_publicacion.desc()
    ).all()


@router.get("/{vacante_id}", response_model=VacanteResponse)
def obtener_vacante(vacante_id: int, db: Session = Depends(get_db)):
    vacante = db.query(Vacante).filter(
        Vacante.id == vacante_id
    ).first()

    if not vacante:
        raise HTTPException(
            status_code=404,
            detail="La vacante no existe"
        )

    return vacante

@router.put("/{vacante_id}", response_model=VacanteResponse)
def actualizar_vacante(
    vacante_id: int,
    datos: VacanteCreate,
    db: Session = Depends(get_db)
):
    vacante = db.query(Vacante).filter(
        Vacante.id == vacante_id
    ).first()

    if not vacante:
        raise HTTPException(
            status_code=404,
            detail="La vacante no existe"
        )

    datos_actualizados = datos.model_dump(exclude_unset=True)

    for campo, valor in datos_actualizados.items():
        setattr(vacante, campo, valor)

    db.commit()
    db.refresh(vacante)

    return vacante    




@router.post(
    "/{vacante_id}/habilidades",
    response_model=VacanteHabilidadResponse,
    status_code=201
)
def asociar_habilidad_vacantes(
    vacante_id: int,
    datos: VacanteHabilidadCreate,
    db: Session = Depends(get_db)
):
    vacante = db.query(Vacante).filter(
        Vacante.id == vacante_id
    ).first()

    if not vacante:
        raise HTTPException(
            status_code=404,
            detail="La vacante no existe"
        )

    habilidad = db.query(Habilidad).filter(
        Habilidad.id == datos.habilidad_id
    ).first()

    if not habilidad:
        raise HTTPException(
            status_code=404,
            detail="La habilidad no existe"
        )

    asociacion_existente = db.query(VacanteHabilidad).filter(
        VacanteHabilidad.vacante_id == vacante_id,
        VacanteHabilidad.habilidad_id == datos.habilidad_id
    ).first()

    if asociacion_existente:
        raise HTTPException(
            status_code=409,
            detail="Esta habilidad ya está asociada a la vacante"
        )

    asociacion = VacanteHabilidad(
        vacante_id=vacante_id,
        habilidad_id=datos.habilidad_id,
        nivel_requerido=datos.nivel_requerido
    )

    db.add(asociacion)
    db.commit()
    db.refresh(asociacion)

    return asociacion

@router.get(
        "/{vacante_id}/habilidades",
        response_model=list[VacanteHabilidadResponse]
)
def listar_habilides_vacante(
    vacante_id: int,
    db: Session = Depends(get_db)
):
    vacante = db.query(Vacante).filter(
        Vacante.id == vacante_id
    ).first

    if not vacante:
        raise HTTPException(
            status_code=404,
            detail="La vacante no existe"
        )

    return db.query(VacanteHabilidad).filter(
        VacanteHabilidad.vacante_id == vacante_id
    ).all()

@router.delete(
        "/{vacante_id}/habilidades/{habilidad_id}"
)
def eliminar_habilidad_vacante(
    vacante_id: int,
    habilidad_id: int,
    db: Session = Depends(get_db)
):
    asociacion = db.query(VacanteHabilidad).filter(
        VacanteHabilidad.vacante_id == vacante_id,
        VacanteHabilidad.habilidad_id == habilidad_id
    ).first()

    if not asociacion:
        raise HTTPException(
            status_code=404,
            detail="La habilidad no esta asociada a esta vacante"
        )

    db.delete(asociacion)
    db.commit()

    return {
        "mensaje": "Habilidad eliminada de la vacante correctamente",
        "vacante_id": vacante_id,
        "habilidad_id": habilidad_id
    }

@router.delete("/{vacante_id}")
def eliminar_vacante(
    vacante_id: int,
    db: Session = Depends(get_db)
):
    vacante = db.query(Vacante).filter(
        Vacante.id == vacante_id
    ).first()

    if vacante is None:
        raise HTTPException(
            status_code=404,
            detail="La vacante no existe"
        )

    db.query(VacanteHabilidad).filter(
        VacanteHabilidad.vacante_id == vacante_id
    ).delete(synchronize_session=False)

    db.delete(vacante)
    db.commit()

    return {
        "mensaje": "Vacante eliminada correctamente",
        "vacante_id": vacante_id
    }


