import argparse
from kubernetes import config, dynamic
from kubernetes.client import api_client
import pkg.consumer as updater


def init():
    parser = argparse.ArgumentParser(description='Update configmap with pmml file location')
    parser.add_argument('--configmap-name', help='configmap name', type=str)
    parser.add_argument('--configmap-namespace', help='configmap namespace', type=str)
    parser.add_argument('--deployment-name', help='deployment to restart', type=str)
    parser.add_argument('--deployment-namespace', help='deployment namespace', type=str)
    parser.add_argument('--kafka-bootstrap-servers', help='comma separated list of brokers',
                        type=lambda s: [str(item) for item in s.split(',')])
    parser.add_argument('--kafka-topic-name', help='topic name to consume messages from', type=str)

    args = parser.parse_args()

    pmml_updater = updater.PmmlUpdater(configmap_name=args.configmap_name,
                                       configmap_namespace=args.configmap_namespace,
                                       kafka_bootstrap_servers=args.kafka_bootstrap_servers,
                                       kafka_topic_name=args.kafka_topic_name,
                                       deployment_name=args.deployment_name,
                                       deployment_namespace=args.deployment_namespace,
                                       client=dynamic.DynamicClient(
                                           api_client.ApiClient(configuration=config.load_incluster_config())
                                       ))

    pmml_updater.watch_and_update_pmml_filepath()
