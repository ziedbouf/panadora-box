import logging

from .kops import KOPS
from .base import BaseEngine

from pandora.config import current_config


logger = logging.getLogger('pandora.api')
config = current_config()

# @TODO: move this out and use flask current_app config
STATE_MAP = {
    'PROVISIONING': config.get('CLUSTER_PROVISIONING_STATE'),
    'RUNNING': config.get('CLUSTER_OK_STATE'),
    'STOPPING': config.get('CLUSTER_DEPROVISIONING_STATE'),
    'RECONCILING': config.get('CLUSTER_UPDATING_STATE'),
    'ERROR': config.get('CLUSTER_ERROR_STATE')
}


class AwsEngine(BaseEngine):
    """
    Aws elastic compute ec2
    """
    name = 'ec2'
    verbose_name = 'Aws Elastic Compute'

    def __init__(self, cluster, **kwargs):
        """
        Implementation of :func: `pandora.engines.base.BaseEngine.__init__`
        """
        # Call parent init to save cluster on self
        super(AwsEngine, self).__init__(cluster, **kwargs)
        # Client initialization
        if cluster.provider is not 'aws':
            raise ValueError(
                'provider should be gce for GceEngine provisioner')

        self.provider = cluster.provider
        self.cluster_id = str(self.cluster.id)
        self.project_id = cluster.project_id

        self.cluster.save()

        logger.debug('AWS Cluster configuration: {}'.format(
            self.cluster.__dict__))

        self.config = self.cluster.__dict__
        self.client = self._get_client()
        self.cache_timeout = 5*60

    def _get_client(self):
        """
        Initialize KOPS provisionner for AWSEngine
        """
        _client = KOPS(provider=self.provider, config=self.config)
        return _client

    def provision(self):
        if self.cluster.network_policy == 'CALICO' and self.cluster.worker_node_count < 2:
            msg = 'Setting {} Network Policy for the cluster {} denied due to '\
                  'unsupported configuration. The minimal size of the '\
                  'cluster to run network policy enforcement is 2 '\
                  'n1-standard-1 instances'.format(self.cluster.network_policy,
                                                   self.cluster_id)
            logger.error(msg)
            return False, msg

        try:
            self.client.kops_provision()
        except Exception as e:
            msg = 'Creating cluster {cluster_name}, cannot provision the cluster on {provider} '.format(
                cluster_name=self.cluster_name, provider=self.provider)
            logger.exception(msg)
            return False, e

        self.cluster.state = STATE_MAP['PROVISIONING']

        try:
            res = self.cluster.save()
        except Exception as e:
            msg = 'Error creating cluster {cluster_name}, cannot save the cluster to DB \n'.format(
                cluster_name=self.cluster_name)
            logger.error(msg)
            return False, e

        return res

    def deprovision(self):
        try:
            self.client.kops_deprovision()
        except Exception as e:
            msg = 'Error deprovising cluster {cluster_name}, cannot provision the cluster on {provider} '.format(
                cluster_name=self.cluster_name, provider=self.provider)
            logger.exception(msg)
            return False, e

        # @TODO: schedule job to check the state and delete the cluster data as soon as possible
        return True, ''

    def resize(self):

        self.client.kops_resize()
        pass

    def get_cluster_config(self):
        try:
            res = self.client.kops_get_config()
        except Exception as e:
            msg = ''
            logger.error(msg)

        return res
