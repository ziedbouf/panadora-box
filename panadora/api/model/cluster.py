import uuid
import datetime
import logging
import sqlalchemy_utils

from flask import current_app as app

from panadora.api import db, flask_bcrypt
from panadora.config import current_config
from .provisionner import Provisioner

logger = logging.getLogger('panadora_api')
config = current_config()

STATE_MAP = {
    'PROVISIONING': config.get('CLUSTER_PROVISIONING_STATE'),
    'RUNNING': config.get('CLUSTER_OK_STATE'),
    'STOPPING': config.get('CLUSTER_DEPROVISIONING_STATE'),
    'RECONCILING': config.get('CLUSTER_UPDATING_STATE'),
    'ERROR': config.get('CLUSTER_ERROR_STATE')
}


class Cluster(db.Model):
    """ Cluster model for storing cluster related details """

    __tablename__ = 'clusters'
    id = db.Column(sqlalchemy_utils.UUIDType(),
                   primary_key=True, default=uuid.uuid4())
    provider = db.Column(db.String(10), nullable=False, default='manual')
    project_id = db.Column(db.String(20), nullable=True)
    cluster_name = db.Column(db.String(30), nullable=False)
    zone = db.Column(db.String(20), nullable=False)
    master_node_type = db.Column(db.String(20), nullable=False)
    worker_node_type = db.Column(db.String(20), nullable=False)
    master_node_count = db.Column(db.Integer, default=1)
    worker_node_count = db.Column(db.Integer, default=3)
    network_range = db.Column(
        db.String(20), default='10.0.0.0/14', nullable=False)
    network_policy = db.Column(
        db.String(20), default='PROVIDER_UNSPECIFIED', nullable=False)
    network_enabled = db.Column(db.Boolean(), default=False)
    state = db.Column(db.String(30), default='')
    kube_config = db.Column(sqlalchemy_utils.JSONType(), default={})

    def __init__(self, **kwargs):
        if (not kwargs.get('cluster_name', '')
            or not kwargs.get('zone', '')
            or not kwargs.get('master_node_type', '')
            or not kwargs.get('worker_node_type', '')
            ):
            raise ValueError(
                'some variables are missing to provision the cluster')

        if kwargs.get('provider', 'manual') == 'gce' and kwargs.get('project_id', '') == '':
            raise ValueError(
                'project id  needed to provision k8s cluster on gce')

        self.id = uuid.uuid4()
        self.cluster_name = kwargs.get('cluster_name')
        self.zone = kwargs.get('zone')
        self.provider = kwargs.get('provider', 'manual')
        self.project_id = kwargs.get('project_id', '')
        self.master_node_type = kwargs.get('master_node_type', 1)
        self.master_node_count = kwargs.get('master_node_count', 1)
        self.worker_node_type = kwargs.get('worker_node_type')
        self.worker_node_count = kwargs.get('worker_node_count', 3)
        self.network_range = kwargs.get('network_range', '10.0.0.0/14')
        self.network_policy = kwargs.get(
            'network_policy', 'PROVIDER_UNSPECIFIED')
        self.network_enabled = self.network_policy != 'PROVIDER_UNSPECIFIED'

    def get_kubeconfig(self):
        """ Get kube config data of cluster """
        # @TODO: fix this to check for cluster state and retrive cluster config
        # if the cluster successfully gots provisioned
        logger.debug(
            'get cluster {} kube config details'.format(self.cluster_name))
        return self.kube_config

    def save(self):
        """ Save cluster to DB """
        logger.debug('saving cluster {} to database'.format(self.cluster_name))
        return True, ''

    def delete(self):
        """ Delete cluster from DB """
        logger.debug(
            'deleting cluster {} from database'.format(self.cluster_name))
        return True, ''

    def update_state(self):
        """ Check for cluster state """
        logger.debug(
            'updating cluster {} details in database'.format(self.cluster_name))
        return True, ''
