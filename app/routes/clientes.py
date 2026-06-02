from flask import Blueprint

bp = Blueprint("clientes", __name__)


@bp.route("/")
def index():
    return """
    <html>
        <head>
            <title>Clientes</title>
        </head>
        <body>
            <h1>ShieldFort - Clientes</h1>
            <p> Carlos Reis carlos.reis@gmail.com</p>
            <p> Guilherme Dantas guilherme.dantas@gmail.com</p>
            <p> Roseanne Maia roseannemaia@gmail.com</p>
            <p> Tereza Dias tereza.dias@gmail.com</p>
        </body>
    </html>
    """
