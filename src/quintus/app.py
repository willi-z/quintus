from flask import Flask

from quintus.server import material
from quintus.server import start


app = Flask(__name__)

app.register_blueprint(start.start_page)
app.register_blueprint(material.material_page, url_prefix="/material")
