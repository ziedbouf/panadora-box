from flask import request
from flask_restplus import Resource
from pandora.api.utils.dto import GceDto
from pandora.api.service import GceService

api = GceDto.api
_cluster = GceDto.cluster


@api.route('/')
class ClusterList(Resource):

    @api.doc('list all provisioned cluster using pandora')
    @api.marshal_list_with(_cluster)
    def get(self):
        """ List all the deployed cluster"""
        return ''

    @api.doc('Provision gce cluster')
    @api.expect(_cluster)
    @api.marshal_with(_cluster, code=201)
    def post(self):
        """ Provision cluster"""
        data = {
            'cluster_name': 'just-a-cluster',
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
        _service = GceService(provider='gce', data=data)
        _service.fake_provision()
        return '', 201


@api.route('/<cluster_id>')
@api.response(404, 'Cluster not found')
@api.param('cluster_id', 'Cluster identifier')
class Cluster(Resource):

    @api.doc('get details of specfic gce cluster')
    def get(self, cluster_id):
        """ Get details of specific cluster """
        pass

    @api.expect(_cluster)
    @api.marshal_with(_cluster, code=201)
    def put(self, cluster_id):
        return ''

    @api.doc('delete gce cluster')
    @api.response(204, 'Cluster deleted')
    def delete(self, cluster_id):
        """ Delete cluster using identifer """
        return '', 204
