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

        self.env = self._get_env()

    def _get_env(self):
        _env = {
            'KOPS_STATE_STORE': self.state_file_path,
            'ZONE': '${{MASTER_ZONES:-"{}"}}'.format(self.config['zone']),
            'NAME': self.config['name']
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

    def provision(self):
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
        logger.info('provison gce cluster using KOPS')
        logger.info('Provisioning the cluster {}'.format(
            self.config['name']))

        result = subprocess.run(
            ['kops',
             'create',
             'cluster',
             '--master-zones',
             'us-east-1',
             '--node-count  3',
             '--image "ubuntu-os-cloud/ubuntu-1604-xenial-v20170202"',
             '--project',
             'test-panadora',
             '--name',
             'just-a-cluster',
             '--yes'],
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
            shell=False,
            env=self.env)

        if result.returncode == 0:
            logger.info(result.stdout)
            return True, None
        else:
            msg = 'Cannot provision the cluster: {} from provider {} using KOPS'.format(
                self.config['id'], self.provider)
            logger.info(msg)

            if result.stderr:
                logger.info(result.stderr)

            return False, msg

        return True, ''

    def deprovision(self):
        """ Deprovision/Delete cluster usign
        kops delete cluster --name=k8s.cluster.site --yes
        """
        logger.info('deprovision/delete gce cluster using KOPS')
        try:
            logger.info('we start deprovisoning/deleting the cluster {}'.format(
                self.config['name']))
            result = subprocess.run(
                ['KOPS', 'help', 'delete', 'cluster'], stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=False, check=True)

            if result.returncode == 0:
                logger.info(result.stdout)
                return True, None

            else:
                msg = 'Cannot provision the cluster: {} from provider {} using KOPS'.format(
                    self.config['id'], self.provider)
                logger.error(msg)
                if result.stderr:
                    logger.error(result.stderr)

                return False, msg
        except (OSError, CalledProcessError) as e:
            msg = 'Cannot provision the cluster: {} from provider {} using KOPS'.format(
                self.config['id'], self.provider)
            logging.error(msg)
            return False, msg
        else:
            msg = 'Provisionned cluster: {} from provider {} using KOPS'.format(
                self.config['id'], self.provider)
            logging.info(msg)

        return True, ''

    def resize(self):
        pass

    def get_config(self):
        pass

    def edit(self):
        pass

    def upgrade(self):
        pass

    def validate(self):
        pass
