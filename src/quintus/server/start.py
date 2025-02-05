from flask import Blueprint, render_template, abort

start_page = Blueprint("start_page", 
                          __name__,
                          template_folder="templates")

@start_page.route("/")
def start():
    return render_template('start/index.html')