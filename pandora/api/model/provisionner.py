import os
import datetime
import logging

from datetime import timedelta
from importlib import import_module

from sqlalchemy_utils import JSONType
from flask import current_app as app

from panadora.api import db, flask_bcrypt
from panadora.config import current_config

config = current_config()


logger = logging.getLogger('panadora_api')

class Provisioner(db.Model):
  """ Provisioner Model for storing provisionner details """
  __tablename__ = "provisioner"
  
  id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
  name = db.Column(db.String(20), nullable=False)
  verbose_name = db.Column(db.String(256), nullable=False)
  engine =  db.Column(db.String(256), nullable=False)
  state = db.Column(db.String(20), nullable=False, default=config.get('PROVISIONER_UNKNOWN_STATE'))
  # @TOOD check the encrpytion of json type using sqlalchemy_utils encrypted types
  parameters = db.Column(JSONType, default={})
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  @classmethod
  def list_engines(cls, self):
    """ Read engines and filter them according to whitelist """
    engines = config.get('PROVISIONER_ENGINE_WHITELIST')

    if engines is None:
      from panadora.engines import all as engines_availables
      engines=  engines_availables

    return engines


  def get_engine_cls(self):
    """ Return engine class. """
    try:
      module_path = 'panadora.engines'.join(self.engine.split('.'))
      class_name = self.engine.split('.')[:-1]
      module = import_module(module_path)
      _class = getattr(module, class_name)
    except Exception as e:
      logger.exception('Error during ')
      _class = None
    
    return _class


  def engine_status(self, save=True):
    state = app.config.get('PROVISIONER_UNKNOWN_STATE')
    engine_class = self.get_engine_cls()

    if engine_class:
      state = engine_class.engine_status(**self.parameters)

    if save:
      self.state = state
      self.save(check_status=False)

    return False


  def save(self, check_status=True, **kwargs):
    with app.app_context():
      if check_status:
        self.sate = self.engine_status(save=False)
      self.verbose_name = getattr(self.get_engine_cls(), 'verbose_name', self.engine)

      return super().save(**kwargs)
