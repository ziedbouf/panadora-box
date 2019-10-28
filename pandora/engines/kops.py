import os
import logging
import subprocess
from subprocess import PIPE, CalledProcessError

from flask import current_app as app

logger = logging.getLogger('panadora_api')


class KOPS:

    def __init__(self, provider, config, **kwargs):
        if provider == 'gce' and 'project_id' not in config:
            raise ValueError(
                'for gce provider, project id needed to provision resources')

        self.provider = provider
        self.config = config
        self.state_file_path = kwargs.get(
            'state_file_path', app.config.get('KOPS_STATE_FILE'))

        self.env = self._construct_env()

    def _construct_env(self):
        # @TODO: need to refactor the env variables based on engine
        _env = {
            'KOPS_STATE_STORE': self.state_file_path,
            'ZONE': '${{MASTER_ZONES:-"{}"}}'.format(self.config['zone']),
            'NAME': self.config['cluster_name']
        }

        if self.provider == 'gce':
            _env['KOPS_FEATURE_FLAGS'] = 'AlphaAllowGCE'
            return _env
        elif self.provider == 'aws':
            _env['AWS_ACCESS_KEY_ID'] = '$(aws configure get aws_access_key_id)'
            _env['AWS_SECRET_ACCESS_KEY'] = '$(aws configure get aws_secret_access_key)'
            return _env
        elif self.provider == 'vmware':
            # @TODO: implement the needed export value for vmware
            raise Exception('platform vmware not supported at the moment')
        elif self.provider == 'openstack':
            # @TODO: implement the needed export value for vmware
            raise Exception('platform vmware not supported at the moment')
        else:
            raise Exception(
                'platform {} not supported, please reach admin for more details'.format(self.provider))

    def kops_get_config(self):
        """ Generate kubeconfig file in cluster configs directory """
        try:
            self.kops_validate
        except Exception as e:
            msg = 'cannot export kubeconfig file for cluster {}'.format(
                self.config['cluster_name'])
            logger.error('')
        pass

    def kops_validate(self):
        pass

    def kops_provision(self):
        """  Provision cluster using
        # Create cluster in GCE.
        # This is an alpha feature.
        export KOPS_STATE_STORE="gs://mybucket-kops"
        export ZONES=${MASTER_ZONES:-"us-east1-b,us-east1-c,us-east1-d"}
        export KOPS_FEATURE_FLAGS=AlphaAllowGCE

        kops create cluster kubernetes-k8s-gce.example.com
        --zones $ZONES \
        --master-zones $ZONES \
        --node-count 3
        --project my-gce-project \
        --image "ubuntu-os-cloud/ubuntu-1604-xenial-v20170202" \
        --yes
        """
        logger.info('Start provisioning the cluster {}'.format(
            self.config['cluster_name']))

        command = 'kops create cluster --cloud {provider} --name {cluster_name} --project {project} --zones $ZONES --master-zones $ZONES --node-count {worker_node_count} --image {os_image} --yes'.format(
            cluster_name=self.config['cluster_name'], provider=self.provider, project=self.config['project_id'], worker_node_count=self.config['worker_node_count'], os_image='ubuntu-os-cloud/ubuntu-1604-xenial-v20170202')

        logger.info(
            'executed command to provision the cluster {}'.format(command))

        result = subprocess.run(command, stdout=PIPE, stderr=PIPE,

                                universal_newlines=True, shell=True, env=self.env)

        if result.returncode == 0:
            logger.info(result.stdout)
            return True, None
        else:
            msg = 'Cannot provision the cluster: {id}/{cluster_name} from provider {provider} using KOPS'.format(
                id=self.config['id'], cluster_name=self.config['cluster_name'], provider=self.provider)
            logger.info(msg)

            if result.stderr:
                logger.info(result.stderr)

            return False, msg

        return True, ''

    def kops_deprovision(self):
        """ Deprovision/Delete cluster usign
        kops delete cluster --name=k8s.cluster.site --yes
        """
        logger.info('deprovision/delete gce cluster using KOPS')
        try:
            logger.info('Start provisioning the cluster {}'.format(
                self.config['cluster_name']))

            command = 'kops delete cluster --name {cluster_name}  --yes'.format(
                name=self.config['cluster_name'])

            logger.info(
                'executed command to deprovision the cluster {}'.format(command))

            result = subprocess.run(command, stdout=PIPE, stderr=PIPE,
                                    universal_newlines=True, shell=True, env=self.env)

            if result.returncode == 0:
                logger.info(result.stdout)
                return True, None

            else:
                msg = 'Cannot provision the cluster: {id}/{cluster_name} from provider {provider} using KOPS'.format(
                    id=self.config['id'], cluster_name=self.config['cluster_name'], provider=self.provider)
                logger.error(msg)

                if result.stderr:
                    logger.error(result.stderr)

                return False, msg
        except (OSError, CalledProcessError) as e:
            msg = 'Cannot deprovision the cluster: {} from provider {} using KOPS'.format(
                self.config['id'], self.provider)
            logging.error(msg)
            return False, msg
        else:
            msg = 'Provisionned cluster: {} from provider {} using KOPS'.format(
                self.config['id'], self.provider)
            logging.info(msg)

        return True, ''

    def kops_edit(self):
        pass

    def kops_resize(self):
        pass

    def kops_upgrade(self):
        pass

    def kops_import(self):
        pass
