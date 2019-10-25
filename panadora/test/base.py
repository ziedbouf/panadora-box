
from flask_testing import TestCase

from panadora.api import db
from panadora.server import app
from panadora.config import current_config

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object(current_config('config/testing.py'))
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
