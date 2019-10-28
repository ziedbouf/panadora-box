import uuid
import datetime
import logging
from .base import BaseProvisionnerService

from pandora.engines import GceEngine
from pandora.api.model import Cluster

logger = logging.getLogger('pandora_api')

# @TODO: delete this as soon as possible


class GceService(BaseProvisionnerService):

    def __init__(self, provider, data, **kwargs):
        if provider is not 'gce':
            raise ValueError(
                'provider should be gce for GceEngine provisionner')

        super(GceService, self).__init__(provider, data, **kwargs)
        self.provisioner = self._get_provisioner()

    def _get_provisioner(self):
        return GceEngine(self.cluster)

    def fake_provision(self):
        self.provisioner.provision()
        return True, 'cluster provisioned'
