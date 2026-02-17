from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf.csrf import CSRFProtect

from src.config import Config
from src.database import db

from src.models import User, Pokemon, Type, Favorite, UserAdmin, PokemonAdmin, FavoriteAdmin


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Si es API sin autenticación, lo normal es desactivar CSRF.
    # Si lo mantienes activo, POST/PUT/DELETE desde curl te pueden fallar.
    CSRFProtect(app)

    CORS(app)
    db.init_app(app)
    Migrate(app, db)

    admin = Admin(app, name='Pokemon API', template_mode='bootstrap3')

    class ReadOnlyModelView(ModelView):
        can_create = False
        can_edit = False
        can_delete = False

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(PokemonAdmin(Pokemon, db.session))
    admin.add_view(ReadOnlyModelView(Type, db.session))
    admin.add_view(FavoriteAdmin(Favorite, db.session))

    # ✅ Import y registro del blueprint al final
    from src.routes import api
    app.register_blueprint(api)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=3000)
