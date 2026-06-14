from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # user_loader — Flask-Login usa isso pra recarregar o usuário da sessão
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints (igual ao que você já tem)
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.clientes import bp as clientes_bp
    from app.routes.orcamentos import bp as orcamentos_bp
    from app.routes.vendas import bp as vendas_bp
    from app.routes.instalacoes import bp as instalacoes_bp
    from app.routes.recorrentes import bp as recorrentes_bp
    from app.routes.starlink import bp as starlink_bp
    from app.routes.gastos import bp as gastos_bp
    from app.routes.auth import bp as auth_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clientes_bp, url_prefix="/clientes")
    app.register_blueprint(orcamentos_bp, url_prefix="/orcamentos")
    app.register_blueprint(vendas_bp, url_prefix="/vendas")
    app.register_blueprint(instalacoes_bp, url_prefix="/instalacoes")
    app.register_blueprint(recorrentes_bp, url_prefix="/recorrentes")
    app.register_blueprint(starlink_bp, url_prefix="/starlink")
    app.register_blueprint(gastos_bp, url_prefix="/gastos")
    app.register_blueprint(auth_bp)

    return app