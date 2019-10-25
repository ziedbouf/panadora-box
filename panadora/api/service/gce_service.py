import uuid
import datetime
import logging

from panadora.engines import GceEngine
from panadora.api.model import Cluster

logger = logging.getLogger('panadora_api')


def provision(data):
    data = {
        'name': 'just-a-cluster',
        'zone': 'us-central1-a',
        'provider': 'gce',
        'project_id': 'test-kqueen',
        'master_node_type': 'n1-standard-1',
        'worker_node_type': 'n1-standard-1',
        'master_node_count': 3,
        'worker_node_count': 3,
        'network_range': '10.0.0.0/14',
        'network_policy': 'CALICO',
    }
    cluster = Cluster(**data)
    gce = GceEngine(cluster=cluster)
    gce.provision()
    return 'please check the data output'
