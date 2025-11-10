"""The main module of the web application."""
import werkzeug.datastructures.file_storage
from flask import Flask, render_template, request


app = Flask(__name__)


@app.route("/")
def home(error: str | None = None, status_code: int = 200) -> tuple[str, int]:
    """ Display the application's home page. """
    return render_template("upload.html", error=error), status_code


@app.route("/recommender", methods=["POST"])
def recommender()-> tuple[str, int]:
    """ Read the input file and forward its contents to the agent. """
    f = request.files["file"]
    content = f.read()
    content = str(content, "utf-8")

    error = validate(f, content)
    if error:
        return home(error, 400)

def validate(f: werkzeug.datastructures.file_storage.FileStorage, content: str) -> str | None:
    """Perform validation on the uploaded file."""
    if f.filename == "":
        return "Please upload your grocery list file."
    if f.mimetype != "text/plain":
        return "Please upload a valid text file with extension .txt."
    if len(content.strip()) == 0:
        return "The file is empty."
    return None


if __name__ == "__main__":
    app.run(debug=False)
