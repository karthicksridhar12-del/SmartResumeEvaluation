from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["resume"]

    if file.filename == "":
        return "No file selected"

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

    return "Resume uploaded successfully!"


if __name__ == "__main__":
    app.run(debug=True)