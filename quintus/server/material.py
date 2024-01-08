from flask import Blueprint, render_template, abort, request

material_page = Blueprint("material_page", 
                          __name__,
                          url_prefix="server",
                          static_folder="static",
                          template_folder="templates")

@material_page.route("/", defaults={"material": "new"}, methods=['GET'])
@material_page.route("/<material>")
def change(material):
    if material == "new":
        return render_template('material/index.html')
    else:
        abort(404)

@material_page.route('/', methods=['POST'])
def handle_data():
    print("I got something!")
    content_type = request.headers.get('Content-Type')
    print(content_type)
    if (content_type == 'application/json'):
        json = request.json
        return json
    elif content_type == 'application/x-www-form-urlencoded':
        data = request.form
        return data

    return "<p>Success!</p>"