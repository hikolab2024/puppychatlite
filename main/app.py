from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from langchain_community.llms import Ollama
import logging
import random

app = Flask(__name__)
socketio = SocketIO(app)

# ログの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Gemma2モデルの初期化
try:
    model = Ollama(model="gemma2", base_url="http://localhost:11434")
    logger.info("Ollamaモデルが正常に初期化されました")
except Exception as e:
    logger.error(f"Ollamaモデルの初期化に失敗しました: {str(e)}")
    model = None

# 日本語プロンプトリスト
japanese_prompts = [
    "こんにちは！何か質問はありますか？",
    "日本語で話しましょう。",
    "私は日本語で答えます。",
    "どんなことについて話したいですか？",
    "日本の文化について質問はありますか？",
    "日本語の勉強をしていますか？",
    "日本の食べ物で好きなものは何ですか？",
    "日本の四季について話しましょう。",
    "日本の歴史に興味がありますか？",
    "アニメや漫画について話しましょう。"
]


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(message):
    logger.info(f"メッセージを受信しました: {message}")
    try:
        if model is None:
            raise Exception("Ollamaモデルが初期化されていません")

        # 日本語プロンプトと指示を追加
        prompt = f"以下の質問に日本語で答えてください。できるだけ自然な日本語を使ってください。\n\n質問: {message}\n\n回答: "

        # 応答を生成
        response = model.invoke(prompt)

        # 応答が空か日本語でない場合、プリセットの日本語プロンプトを使用
        if not response or not any("\u3040" <= c <= "\u30ff" for c in response):
            response = random.choice(japanese_prompts)

        logger.info(f"生成された応答: {response}")
        emit('response', {'message': response})
    except Exception as e:
        error_message = f"エラーが発生しました: {str(e)}"
        logger.error(error_message)
        emit('response', {'message': error_message})


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001, allow_unsafe_werkzeug=True)