"""The main module of the web application."""

from flask import Flask, render_template, request
from werkzeug.datastructures.file_storage import FileStorage

from apps.web_app import agent_interface
from apps.agent import orchestrator

grocery_agent = None
app = Flask(__name__)


@app.route("/")
def home(error: str | None = None, status_code: int = 200) -> tuple[str, int]:
    """Display the application's home page."""
    global grocery_agent
    if not grocery_agent:
        grocery_agent = orchestrator.init_agent()

    return render_template("upload.html", error=error), status_code


@app.route("/recommender", methods=["POST"])
def recommender() -> tuple[str, int]:
    """Read the input file and forward its contents to the agent."""
    f = request.files["file"]

    error, filename, content = validate(f)
    if error:
        return home(error, 400)
    return render_template(
        "recommendations.html",
        products=agent_interface.send_to_agent(filename, content, grocery_agent),
    ), 200


def validate(f: FileStorage) -> tuple[str | None, str | None, str | None]:
    """Perform validation on the uploaded file."""
    if f.filename == "":
        return "Please upload your grocery list file.", None, None
    if f.mimetype != "text/plain":
        return "Please upload a valid text file with extension .txt.", None, None

    content = f.read()
    content = str(content, "utf-8")

    if len(content.strip()) == 0:
        return "The file is empty.", None, None
    return None, f.filename, content


if __name__ == "__main__":
    app.run(debug=False)
