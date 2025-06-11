from sqlalchemy.orm import Session

from app.crud import isla as crud_isla
from app.models import Isla


def test_crud_isla(db_session: Session):
    # Insert manual vía modelo
    isla = Isla(id_isla=99, nombre="Isla99", descripcion="Descripción 99")
    db_session.add(isla)
    db_session.commit()

    # list_all
    todas = crud_isla.list_all(db_session)
    assert any(i.id_isla == 99 for i in todas)

    # get_one
    found = crud_isla.get_one(db_session, 99)
    assert found and found.nombre == "Isla99"
