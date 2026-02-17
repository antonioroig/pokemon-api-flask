def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Inicializar bcrypt (NECESARIO para set_password)
    from src.models import bcrypt
    bcrypt.init_app(app)

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

    from src.routes import api
    app.register_blueprint(api)

    return app
