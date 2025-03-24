from db_connection import connect_to_db

def get_questions():
    conn = connect_to_db()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)  # Resultados como diccionarios
    cursor.execute("SELECT * FROM Pregunta")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def create_question(question_text, difficulty, topic, creator, category):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()
    sql = "INSERT INTO Pregunta (textoPregunta, nivelDificultad, tema, creador, categoria) VALUES (%s, %s, %s, %s, %s)"
    values = (question_text, difficulty, topic, creator, category)
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
    return True