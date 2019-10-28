import logging
from panadora.api.model import Cluster

logger = logging.getLogger('panadora_api')


class BaseProvisionnerService:
    """ Base provisionner service object. """
    name = 'base'
    verbose_name = 'Base provisionner service'

    def __init__(self, provider, data, **kwargs):
        self.provider = provider
        self.data = data

        self.cluster = self._get_cluster()
        self.provisionner = self._get_provisioner()

    def _get_cluster(self):
        """ Contruct cluster from data input """
        return Cluster(**self.data)

    def _get_provisioner(self):
        """ Return provisionner related to the provider """
        raise NotImplementedError

    def provision(self):
        """Provision cluster depending on provider """
        try:
            self.cluster.save()
        except Exception as e:
            msg = 'Error on saving cluster to Db'
            logger.error(msg)
            return False, e

        try:
            self.provisioner.provision()
        except Exception as e:
            msg = 'Error on provisioning the cluster'
            logger.error(msg)
            # @TODO: use STATE_MAP
            self.cluster.state = 'ERROR'
            self.cluster.save()
            return False, e

        return True, ''

    def deprovision(self):
        """Provision cluster depending on provider """
        try:
            self.provisioner.deprovision()
            self.cluster.state = ''
        except Exception as e:
            msg = 'Error on provisioning the cluster'
            logger.error(msg)
            return False, e

        # @TODO: schedule job to keep track of cluster state
        # and delte the cluster entities as soon as the cluster
        # got delete
        return True, ''

    def resize(self):
        """ Resize cluster"""
        raise NotImplementedError
