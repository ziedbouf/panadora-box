import os
from flask import Blueprint, Response, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from flask_restplus import Api, Namespace, Resource

from pandora.api.controller.user import api as user_ns
from pandora.api.controller.auth import api as auth_ns
from pandora.api.controller.gce import api as gce_ns
from prometheus_flask_exporter import PrometheusMetrics


blueprint = Blueprint('api', __name__)
api = Api(blueprint,
          title='FLASK RESTPLUS API BOILER-PLATE WITH JWT',
          version='1.0',
          description='a boilerplate for flask restplus web service'
          )

api.add_namespace(user_ns, path='/user')
api.add_namespace(gce_ns)
api.add_namespace(auth_ns)


metrics = PrometheusMetrics(blueprint)


@blueprint.route('/metrics')
def meter():
    from prometheus_client import multiprocess, CollectorRegistry

    if 'prometheus_multiproc_dir' in os.environ:
        registry = CollectorRegistry()
    else:
        registry = metrics.registry

    if 'name[]' in request.args:
        registry = registry.restricted_registry(request.args.getlist('name[]'))

    if 'prometheus_multiproc_dir' in os.environ:
        multiprocess.MultiProcessCollector(registry)

    headers = {'Content-Type': CONTENT_TYPE_LATEST}
    return generate_latest(metrics.registry), 200, headers
