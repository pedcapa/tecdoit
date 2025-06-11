from sqlalchemy.orm import Session

from app.crud import tema as crud_tema


def test_crud_tema(db_session: Session):
    # 1) Create
    tema = crud_tema.create_tema(db_session, "Trigonometría", "Funciones trigonométricas")
    assert tema.id_tema is not None
    assert tema.nombre == "Trigonometría"

    # 2) List
    listado = crud_tema.list_temas(db_session)
    assert any(t.id_tema == tema.id_tema for t in listado)

    # 3) Get one
    single = crud_tema.get_tema(db_session, tema.id_tema)
    assert single and single.nombre == "Trigonometría"

    # 4) Patch
    patched = crud_tema.patch_tema(
        db_session, tema.id_tema, {"descripcion": "Síntesis trigonométrica"}
    )
    assert patched.descripcion == "Síntesis trigonométrica"

    # 5) Delete
    crud_tema.delete_tema(db_session, tema.id_tema)
    assert crud_tema.get_tema(db_session, tema.id_tema) is None
