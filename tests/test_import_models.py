from models import Base


def test_import_models_user():
    from models.users import User

    assert issubclass(User, Base)
    assert User.__name__.lower() == User.__tablename__
