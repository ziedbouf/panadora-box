from flask import request
from flask_restplus import Resource
from panadora.api.utils.dto import GceDto
from panadora.api.service import provisioon_gce

api = GceDto.api
_cluster = GceDto.cluster


@api.route('/')
class ClusterList(Resource):

    @api.doc('list all provisioned cluster using panadora')
    @api.marshal_list_with(_cluster)
    def get(self):
        """ List all the deployed cluster"""
        return ''

    @api.doc('Provision gce cluster')
    @api.expect(_cluster)
    @api.marshal_with(_cluster, code=201)
    def post(self):
        """ Provision cluster"""
        provisioon_gce(data=None)
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
