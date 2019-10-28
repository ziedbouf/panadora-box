
from flask_testing import TestCase

from pandora.api import db
from pandora.server import app
from pandora.config import current_config


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
