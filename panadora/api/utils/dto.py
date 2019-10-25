from flask_restplus import Namespace, fields

class ProvisionerDto:
    api = Namespace('provisioner', description='provisioner related operations')
    provisioner = api.model('provisioner', {
        'name': fields.String(required=True, description='provisioner name'),
        'project_id': fields.String(description='project to use (must be set on GCE'),
        'cloud': fields.String(required=True, description='cloud provider to use - gce, aws, vsphere, openstack'),
        'cloud-labels': fields.String(description='A list of KV pairs used to tag all instance groups in AWS e.g. Owner=John Doe,Team=Some Team')
    })

class GceDto:
    api = Namespace('gce', description='gce cluster related operations')
    # TODO validation of ip address, and maybe use flask-restplus definition of mode using JSON schema 
    # https://flask-restplus.readthedocs.io/en/stable/marshalling.html#define-model-using-json-schema
    cluster = api.model('cluster', {
        'provisioner_id': fields.String(required=True, description='gce provider id'),
        'name': fields.String(required=True, description='ame of cluster. Overrides KOPS_CLUSTER_NAME environment variable'),
        'zone': fields.String(required=True, description='zone used for the cluster'),
        'master_node_type':  fields.String(required=True, description='master node type'),
        'worker_node_type':  fields.String(required=True, description='worker node type'),
        'master_node_count':  fields.Integer(default=3, required=True, description='master node count'),
        'worker_node_count':  fields.Integer(default=2, required=True, description='worker node count'),
        'network_range': fields.String(default='10.0.0.0/14', required=True, description="")
    })

class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(required=True, description='user email address'),
        'username': fields.String(required=True, description='user username'),
        'password': fields.String(required=True, description='user password'),
        'public_id': fields.String(description='user Identifier')
    })


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })
