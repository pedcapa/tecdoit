def test_cleanup_orphans(tmp_path, monkeypatch, db_session):
    from app.management import cleanup_orphans
    monkeypatch.setattr(cleanup_orphans, "STATIC_DIR", tmp_path)
    from app.models import Pregunta
    preg = Pregunta(enunciado="?", tipo="abc", id_isla=1, dificultad=1, randomizar=0, estado="publicada")
    db_session.add(preg)
    db_session.commit()
    pid = preg.id_pregunta
    (tmp_path / "preguntas").mkdir(exist_ok=True)
    (tmp_path / "preguntas" / f"{pid}.png").write_bytes(b"ok")
    (tmp_path / "preguntas" / "9999.png").write_bytes(b"xx")
    cleanup_orphans.main(db_session)
    assert (tmp_path / "preguntas" / f"{pid}.png").exists()
    assert not (tmp_path / "preguntas" / "9999.png").exists()
