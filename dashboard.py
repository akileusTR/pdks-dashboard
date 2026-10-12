from flask import Flask, send_file

app = Flask(__name__)

@app.route("/api/pdks")
def pdks():
    return send_file(
        "data/latest.json",
        mimetype="application/json"
    )

app.run(
    host="0.0.0.0",
    port=5000
)
