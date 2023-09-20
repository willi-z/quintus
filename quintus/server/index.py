from flask import Blueprint, render_template

index_page = Blueprint(
    "index_page", __name__, url_prefix="/", template_folder="templates"
)


@index_page.route("/")
def index():
    return render_template("pages/home.html")
