from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/viewer")
def viewer():
    return render_template("viewer.html")
