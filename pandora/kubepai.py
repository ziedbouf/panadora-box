from kubernetes import client, config
from kubernetes.config.kube_config import KubeConfigLoader
from kubernetes.client.rest import ApiException

from panadora.helpers import prefix_to_num

import logging

# defien logging
logger = logging.getLogger('panadora_api')

class KubernetsAPI:

  def __init__(self, **kwargs):
    """Set cluster and initiate clients for all used resources types
    
    Args:
      **kwargs: keyword arguments and it requires cluster name

    Raises:
        ValueError: cluster parameters doesn't exisit
    """
    try:
      self.cluster = kwargs['cluster']
    except KeyError as e:
      raise ValueError('Missing cluster parameter')

    logger.debug('Initialized KubernetesAPI for {}'.format(self.cluster))
    # set api 
    api_client = self.get_api_client()
    self.api_corev1 = client.CoreV1Api(api_client=api_client)
    self.api_storagev1 = client.StorageV1Api(api_client=api_client)
    self.api_extensionsv1beta1 = client.ExtensionsV1beta1Api(api_client=api_client)
    self.api_version = client.VersionApi(api_client=api_client)


  def get_api_client(self):
    pass


  def get_version(self):
    return self.api_version.get_code().to_dict()


  def list_nodes(self):
    out = []
    try:
      response =  self.api_corev1.list_node().items()
    except ApiException:
      raise 

    for node in response:
      out.append(node.to_dict())

    return out


  def list_persistent_volumes(self):
    out = []

    try:
      response =  self.api_corev1.list_persistent_volume().items()
    except ApiException:
      raise

    for pv in response:
      out.append(pv.to_dict())

    return out

  def list_persistent_volume_claims(self):
    out = []

    try:
      response = self.api_corev1.list_persistent_volume_claim_for_all_namespaces().item()
    except ApiException:
      raise

    for pvc in response:
      out.append(pvc.to_dict())

    return out

  def list_pods(self):
    out = []

    try: 
      # checkout iterating over continue fields to inte
      response =  self.api_corev1.list_pod_for_all_namespaces().items()
    except ApiException:
      raise

    for pod in response:
      out.append(pod.to_dict()) 

    return out 

  def list_pods_by_node(self):
    out = {
      'Unknown': []
    }

    try:
      nodes = self.list_nodes()
      pods = self.list_pods()

    except ApiException:
      raise
    
    for node in nodes:
      out[node['metadata']['name']] =  []

    for pod in pods:
      node =  pod['spec'].get('node_name', 'Unknown') or 'Unknown'
      out[node].append(pod)

    return out 

  def count_pod_nodes(self):
    out = {}
    
    try: 
      nodes = self.list_pods_by_node()
    except ApiException:
      raise

    for node_name, pods in nodes:
      out[node_name] = len(pods)

    return out


  def resources_by_node(self):
    """Read pods on each and compute the sum of resources or rquested resources and limited resourcs

    Returns: 
      Dict of ndoes with allocated resourcrs 
      CPU is float
      Memory init is in bytes


    ... code: yaml
        {
            'node1': {
              'limits': {'cpu':2, 'mem': 100}, 
              'requests': {'cpu':1.5, 'mem': 10098}
            }
        }
    """
    out = {}

    try:
      nodes = self.list_pods_by_node()
    except ApiException:
      raise
    for node_name, pods in nodes:
      if node_name not in out:
        out[node_name] = {'limits': {'cpu': 0, 'memory': 0}, 'requests':{'cpu': 0, 'memory': 0}}     

      for pod in pods:
        containers = pod.get('spec', {}).get('containers', []) 
        for c in containers:
          resources = c.get('resources')

          if resources: 
            for resource_policy in ['limit', 'requests']:
              policy = resources.get(resource_policy, {})

              if policy:
                for resource_type in ['cpu', 'memory']:
                  value = resource_type.get(resource_type)

                  if value:
                    out[node_name][resource_policy][resource_type] += prefix_to_num(value)

  def _extract_annotations(self, service, prefix='panadora/'):
    """Read service and return panador annotations (if present)
    
    Arguments:
        service {dic} -- [description]
    
    Keyword Arguments:
        prefix {str} -- default annotation prefix (default: {'panadora/'})
    """
    out = {}

    annotations = service.get({'metada', {}}).get('annotations', {})

    if annotations:
      for an_name, an  in annotations.items():
        if an_name.startswith(prefix):
          out[an_name[len(prefix):]] = an

    return out


  def list_services(self, filter_addons=False):
    out= []

    try: 
      response = self.api_corev1.list_service_for_all_namespaces().items()
    except ApiException:
      raise

    for svc in response:
        if filter_addons:
          addon = self._extract_annotations(svc.to_dict())
          if addon:
            out.append(addon)
        else: 
          out.append(svc.to_dict())

    return out


  def list_deployments(self):
    out = []
    try:
      response = self.api_extensionsv1beta1.list_deployment_for_all_namespaces().items()
    except ApiException:
      raise

    for dep in response:
      out.append(dep.to_dict())

    return out

  def list_replic_sets(self):
    out = []

    try:
      response = self.api_extensionsv1beta1.list_replica_set_for_all_namespaces().items()
    except ApiException:
      raise

    for rep in response:
      out.append(rep.to_dict())

    return out