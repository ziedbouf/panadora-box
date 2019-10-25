from panadora.config import current_config

import logging

config = current_config()
logger = logging.getLogger('panadora_api')


class BaseEngine:
    """Base engine object.

    When you initialize the engine through the prepared property: func: `~panadora.models.Cluster.engine`
    on :obj:`panadora.models.Cluster` model object, all keys in engine object parameters attribute (JSONField) on
    :obj:`panadora.models.Provisoner` obeject are passed as kwargs

    Examples::
        >>> print my_provisioner.parameters
        {'username': 'foo', 'password': 'bar'}
        >>> print my_cluster.engine.conn_kw
        {'username': 'foo', 'password': 'bar'}

    Arguments:
      cluster {:obj:`panadora.models.Cluster`} -- Cluster model object related to the engine instance
      **kwargs: keyword arguments specific to Provisionner implementation

    Attributes:
      cluster {:obj:`panadora.models.Cluster`} -- Cluster model object related to the engine instance
      name {str} -- NAme of the engine usable by program
      verbose_name {str} --  Human readable name of the engine
      parameter_schema (dict): Dictionary representation of the parameters with hints for form rendering.::
          {
            'provisioner': {
                'username': {
                    'type': 'text',
                    'validators': {
                        'required': True
                    }
                },
                'password': {
                    'type': 'password',
                    'validators': {
                        'required': True
                    }
                }
            }
            'cluster': {
                'node_count': {
                    'type': 'integer',
                    'validators: {
                        'required': True
                    }
                }
            }
          }
    """
    name = 'base'
    verbose_name = 'Base Engine'
    parameter_schema = {}

    def __init__(self, cluster, **kwargs):
        self.cluster = cluster

    def list_clusters(self):
        """ Get all cluster available on backend

        Returns:
          list: list of dictionaries. Dictionary format should be::
              {
                  'key': key,     # this record should be cached under this key if you choose to cache
                  'name': name,   # name of the cluster in its respective backend
                  'id': id,       # id of `panadora.models.Cluster` object in Panadora database if cluster managed by Panadora,
                                    otherwise None
                  'state': state, # cluster.state
                  'metadata': {
                      'foo': bar  # any keys specific for the Provisioner implementation
                  }
              }
        """
        raise NotImplementedError

    def get_cluster(self):
        """ Get single cluster from backend related to the engine instance

        Althougth this function doesn't take any arguments, it is expected that 
        the implementation of the provisioner gts `self.cluster` to provide
        the target cluster for which data is needed

        Returns: 
          dict: Dictionnary format should be::

            {
              'key': key,     # (str) this record should be cached under this key if you choose to cache
              'name': name,   # (str) name of the cluster in its respective backend
              'id': id,       # (str or UUID) id of `Panadora.models.Cluster` object in Panadora database
              'state': state, # (str) state of cluster on backend represented by app.config['CLUSTER_[FOO]_STATE']
              'metadata': {
                  'foo': bar  # any keys specific for the Provisioner implementation
              }
            }
        """
        raise NotImplementedError

    def provision(self):
        """ Provision the cluster related to the engine instance to backend

        Although this function doesn't ttake any arugemnts, it is expected that 
        the implementation of the provisionner gets `self.cluster` to provide the 
        relevant object which we want to provision to backend

        Returns:
          tuple: First item is bool (success/failure), second item is error, can be None::
            (True, None)                            # succed to provision
            (False, 'Cou t not connect to backend') # failed to provision
        """
        raise NotImplementedError

    def deprovision(self):
        """ Deporvision the cluster related to the engine instance from backend

        Although this function doesn't ttake any arugemnts, it is expected that 
        the implementation of the provisionner gets `self.cluster` to provide the 
        relevant object which we want to deprovision to backend.

        Returns:
                tuple: First item is bool (success/failure), second item is error, can be None::
                    (True, None)                            # succed to provision
                    (False, 'Could not connect to backend') # failed to provision
        """
        raise NotImplementedError

    def resize(self, node_count):
        """ Resize the cluster related to the engine instance from backend

        Although this function doesn't ttake any arugemnts, it is expected that 
        the implementation of the provisionner gets `self.cluster` to provide the 
        relevant object which we want to resize.

        Returns:
                tuple: First item is bool (success/failure), second item is error, can be None::
                    (True, None)                            # succed to resize
                    (False, 'Could not connect to backend') # failed to resize
        """
        raise NotImplementedError

    def set_cluster_network_policy(self):
        """ Set specific network policy to the cluster related to the engine instance.

        Arguements: 
          network_provider {str} -- Name oof supported network provider/addon
          enabled {bool} --  Enable/Disable policy

        Returns:
          tuple: First item is bool (success/failure), second item is error, can be None::
                    (True, None)                            # succed update policy
                    (False, 'error_message')                # failed to update policy, error description

        """
        raise NotImplementedError

    def get_cluster_config(self):
        """Get kubeconfig of the cluster related to this engine from backend.

        Although this function doesn't take any arguments, it is expected that
        the implementation of the Provisioner gets ``self.cluster`` to provide the
        relevant object which we want to get kubeconfig for.

        Returns:
            dict: Dictionary form of kubeconfig (`yaml.load(kubeconfig_file)`)
        """
        raise NotImplementedError

    def get_progress(self):
        """Get progress of provisioning if its possible to determine.

        Although this function doesn't take any arguments, it is expected that
        the implementation of the Provisioner gets ``self.cluster`` to provide the
        relevant object which we want to get provisioning progress for.
        Returns:
            dict: Dictionary representation of the provisioning provress.::
                {
                    'response': response, # (int) any number other than 200 means failure to determine progress
                    'progress': progress, # (int) provisioning progress in percents
                    'result': result      # (str) current state of the cluster, i.e. 'Deploying'
                }
          """
        raise NotImplementedError

    @classmethod
    def get_parameter_schema(cls):
        """Return parameters specific for this Provisioner implementation.

        This method should return parameters specific to the Provisioner implementation,
        these are used to generate form for creation of Provisioner object and are stored
        in parameters attribute (JSONField) of the `panadora.models.Provisioner` object.

        Returns:
            dict:  Returns ``self.parameter_schema`` in default, but can be overridden.
        """
        if not hasattr(cls, 'parameter_schema'):
            raise NotImplementedError(
                'parameter_schema attribute should be privided in the provisionner class implementation')

        return cls.parameter_schema

    @classmethod
    def engine_status(cls, **kwargs):
        """Check if backend this Provisioner implements is reachable and/or working.

        Returns:
            str: Return status of engine, should use statuses from ``app.config``
        """
        return config.get('PROVISIONNER_OK_STATE')
