from flask import Flask, render_template, request, send_file
from generate import draw_certificate
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        cert_type = request.form["cert_type"]
        event_title = request.form["event_title"]
        event_date = request.form["event_date"]

        pdf_path = draw_certificate(name, cert_type, event_title, event_date)
        return send_file(pdf_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
