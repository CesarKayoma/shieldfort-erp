from flask import Blueprint

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    return """
    <html>
        <head>
            <title>Dashboard</title>
        </head>
        <body>
            <h1>ShieldFort - Home</h1>
            <p>Serviços Realizados 20</p>
            <p>Valor Faturado R$ 3.697,50</p>
            <p>Total Clientes 16</p>
            <p>Vendas Mês Atual 18</p>
        </body>
    </html>
    """
