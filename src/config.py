import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    WTF_CSRF_ENABLED = False

    # 1) Prioriza DB remota (Postgres) si existe variable de entorno
    DB_URL = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
    )

    if DB_URL:
        # SQLAlchemy prefiere "postgresql://"
        if DB_URL.startswith("postgres://"):
            DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DB_URL
    else:
        # 2) Fallback local (solo para desarrollo)
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        INSTANCE_DIR = os.path.join(os.path.dirname(BASE_DIR), "instance")
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'pokemon.db')}"
