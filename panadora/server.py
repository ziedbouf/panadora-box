import os
import unittest

from panadora import blueprint
from panadora.api import create_app, db
from panadora.api.model import User, UserRoles, Role, BlacklistToken, Organization, Cluster, Provisioner

from flask_user import UserManager
from flask_migrate import Migrate, MigrateCommand, init


app = create_app(os.getenv('FLASK_ENV') or 'development')
app.register_blueprint(blueprint)
user_manager = UserManager(app, db, User)
migrate = Migrate(app, db)


@app.cli.command("test")
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    app.run()
