from flask import Flask, jsonify, request
from db_queries import get_questions, create_question

app = Flask(__name__)

@app.route('/questions', methods=['GET'])
def questions():
    questions = get_questions()
    if questions:
        return jsonify(questions)
    else:
        return jsonify({'error': 'Database error'}), 500

@app.route('/newquestion', methods=['POST'])
def newquestion():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    text = data.get('text')
    difficulty = data.get('difficulty')
    topic = data.get('topic')
    creator = data.get('creator')
    category = data.get('category')
    success = create_question(text, difficulty, topic, creator, category)

    if success:
      return jsonify({'message': 'question created'}),201
    else:
      return jsonify({'error':'database error'}), 500

if __name__ == '__main__':
    app.run(debug=True)