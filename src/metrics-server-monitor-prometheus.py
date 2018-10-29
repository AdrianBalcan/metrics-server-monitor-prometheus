from flask import Flask, Response
from prometheus_client import Gauge, generate_latest
import re
import json
import urllib
import ssl
import pprint

pods_cpu = Gauge('metrics_server_pod_cpu_usage', 'Metrics server pod cpu utilization', labelnames=['namespace', 'pod', 'container'])
pods_memory = Gauge('metrics_server_pod_memory_usage', 'Metrics server pod memory utilization', labelnames=['namespace', 'pod', 'container'])
nodes_cpu = Gauge('metrics_server_node_cpu_usage', 'Metrics server node cpu utilization', labelnames=['instance'])
nodes_memory = Gauge('metrics_server_node_memory_usage', 'Metrics server node memory utilization', labelnames=['instance'])

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Usage Metrics from metrics-server</h1> <br><br> <a href="/metrics">Metrics</a><br><a href="/healthz">Healthz</a>'

@app.route('/healthz/')
def healthz():
    return 'ok'

@app.errorhandler(500)
def handle_500(error):
    return str(error), 500

@app.route('/metrics')
def metrics():
  pods_cpu._metrics.clear()
  pods_memory._metrics.clear()
  pods_url = 'https://metrics-server.kube-system/apis/metrics.k8s.io/v1beta1/pods'
  nodes_url = 'https://metrics-server.kube-system/apis/metrics.k8s.io/v1beta1/nodes'
  pods = json.load(urllib.urlopen(pods_url, context=ssl._create_unverified_context()))
  nodes = json.load(urllib.urlopen(nodes_url, context=ssl._create_unverified_context()))
  for pod in pods['items']:
    for container in pod['containers']:
      pods_cpu.labels(namespace=pod['metadata']['namespace'], pod=pod['metadata']['name'], container=container['name']).set(re.sub("\D", "", container['usage']['cpu']))
      pods_memory.labels(namespace=pod['metadata']['namespace'], pod=pod['metadata']['name'], container=container['name']).set(re.sub("\D", "", container['usage']['memory']))
  for node in nodes['items']:
    nodes_cpu.labels(instance=node['metadata']['name']).set(re.sub("\D", "", node['usage']['cpu']))
    nodes_memory.labels(instance=node['metadata']['name']).set(re.sub("\D", "", node['usage']['memory']))
  return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9100)
