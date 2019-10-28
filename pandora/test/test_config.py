import os
import unittest

from flask import current_app
from flask_testing import TestCase

from pandora.server import app
from pandora.config import current_config, basedir


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object(current_config('config/testing.py'))
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['SECRET_KEY'] is 'my_precious')
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///' +
            os.path.join(basedir, 'db/t_pandora.db')
        )


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object(current_config('config/development.py'))
        return app

    def test_app_is_development(self):
        self.assertFalse(app.config['SECRET_KEY'] is 'my_precious')
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///' +
            os.path.join(basedir, 'db/pandora.db')
        )


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object(current_config('config/production.py'))
        return app

    def test_app_is_production(self):
        self.assertTrue(app.config['DEBUG'] is False)


if __name__ == '__main__':
    unittest.main()
