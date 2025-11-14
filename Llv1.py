from flask import Flask, render_template_string, session, request, jsonify
from janome.tokenizer import Tokenizer
import random
import string

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
tokenizer = Tokenizer()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Japanese Phrase Sorting Quiz</title>
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
    <style>
        body {
            font-family: 'Hiragino Sans', 'Noto Sans JP', sans-serif;
            margin: 40px;
            background: #f9fbfd;
            color: #333;
            text-align: center;
        }
        h1 {
            color: #1f4e78;
            margin-bottom: 10px;
        }
        p {
            font-size: 1.1em;
        }
        .word-list {
            display: inline-flex;
            gap: 8px;
            flex-wrap: wrap;
            padding: 15px;
            border: 2px solid #d0e3f0;
            border-radius: 10px;
            background: #ffffff;
            min-height: 50px;
            margin-top: 20px;
        }
        .word {
            background: #e0f0ff;
            padding: 8px 14px;
            border-radius: 8px;
            cursor: grab;
            font-size: 1.1em;
            transition: background 0.2s;
        }
        .word:hover {
            background: #cde6ff;
        }

        /* ===== ボタン ===== */
        .button-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 25px;
            gap: 12px;
        }

        .main-btn {
            background: #4da3ff;
            color: white;
            font-size: 1.2em;
            padding: 12px 36px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.3s, transform 0.1s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.20);
        }
        .main-btn:hover {
            background: #368ff0;
            transform: scale(1.3);
        }

        .sub-btn {
            background: #eef6ff;
            color: #1f4e78;
            font-size: 1em;
            padding: 8px 20px;
            border: 1px solid #a8c9e8;
            border-radius: 15px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .sub-btn:hover {
            background: #d8eaff;
        }

        #result {
            font-weight: bold;
            margin-top: 20px;
            font-size: 1.1em;
        }

        #answer {
            font-weight: bold;
            color: #444;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Japanese Phrase Sorting Quiz</h1>
    <p>Sort words correctly</p>

    <div id="word-list" class="word-list">
        {% for token in tokens %}
            <div class="word" draggable="true">{{ token }}</div>
        {% endfor %}
    </div>

    <!-- ボタン -->
    <div class="button-container">
        <button class="main-btn" id="check-btn" onclick="checkAnswer()">正解を確認</button>
        <button class="sub-btn" id="show-answer" onclick="revealAnswer()">答えを表示</button>
        <button class="sub-btn" id="new-question" onclick="newQuestion()">もう一問出す</button>
    </div>

    <p id="result"></p>
    <p id="answer"></p>

    <script>
        const list = document.getElementById('word-list');
        new Sortable(list, { animation: 150 });

        function checkAnswer() {
            const words = Array.from(list.children).map(el => el.textContent);
            fetch('/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answer: words })
            })
            .then(response => response.json())
            .then(data => {
                const result = document.getElementById('result');
                result.textContent = data.correct ? "Correct!" : "Incorrect";
                result.style.color = data.correct ? "green" : "red";
            });
        }

        function revealAnswer() {
            fetch('/reveal')
            .then(response => response.json())
            .then(data => {
                document.getElementById('answer').textContent = "正解：" + data.answer;
            });
        }

        function newQuestion() {
            window.location.reload();
        }
    </script>
</body>
</html>
"""

# ------------------------------
# 自動生成ロジック
# ------------------------------
TEMPLATES = [
    "{time}に友だちと{activity}をしました。",
    "{place}で{object}を見つけて驚きました。",
    "{subject}は{adjective}ので、{activity}をやめました。",
    "昨日の{time}、{place}へ{activity}に行きました。"
]

KEYWORDS = {
    "time": ["朝", "午後", "夜", "昼休み"],
    "activity": ["読書", "散歩", "映画鑑賞", "買い物", "勉強"],
    "place": ["公園", "図書館", "駅前", "カフェ", "海辺"],
    "object": ["本", "鳥", "虹", "写真", "花"],
    "subject": ["私は", "彼は", "彼女は", "先生は"],
    "adjective": ["忙しい", "寒い", "静か", "楽しい"]
}

def generate_sentence():
    template = random.choice(TEMPLATES)
    sentence = template.format(
        time=random.choice(KEYWORDS["time"]),
        activity=random.choice(KEYWORDS["activity"]),
        place=random.choice(KEYWORDS["place"]),
        object=random.choice(KEYWORDS["object"]),
        subject=random.choice(KEYWORDS["subject"]),
        adjective=random.choice(KEYWORDS["adjective"])
    )
    return sentence

@app.route("/")
def index():
    original_text = generate_sentence()
    tokens = [token.surface for token in tokenizer.tokenize(original_text) if token.surface.strip()]
    shuffled_tokens = tokens.copy()
    random.shuffle(shuffled_tokens)
    session["correct_order"] = tokens
    session["original_text"] = original_text
    return render_template_string(HTML_TEMPLATE, tokens=shuffled_tokens)

@app.route("/check", methods=["POST"])
def check_answer():
    user_answer = request.json.get("answer", [])
    correct_answer = session.get("correct_order", [])
    is_correct = user_answer == correct_answer
    return jsonify({"correct": is_correct})

@app.route("/reveal")
def reveal():
    correct_sentence = session.get("original_text", "")
    return jsonify({"answer": correct_sentence})

if __name__ == "__main__":
    app.run(debug=True)
