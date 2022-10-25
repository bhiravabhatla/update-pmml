import pdb

from kafka import KafkaConsumer
from kubernetes.client.rest import ApiException
import datetime


class PmmlUpdater:

    def __init__(self, configmap_name, configmap_namespace, deployment_name, deployment_namespace,
                 kafka_bootstrap_servers, kafka_topic_name, client):
        self.configmap_name = configmap_name
        self.configmap_namespace = configmap_namespace
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic_name = kafka_topic_name
        self.deployment_name = deployment_name
        self.deployment_namespace = deployment_namespace
        self.client = client

    def restart_deployment(self):
        api = self.client.resources.get(api_version="apps/v1", kind="Deployment")
        now = datetime.datetime.utcnow()

        now = str(now.isoformat("T") + "Z")
        body = {
            'spec': {
                'template': {
                    'metadata': {
                        'annotations': {
                            'kubectl.kubernetes.io/restartedAt': now
                        }
                    }
                }
            }
        }
        try:
            print("restarting deploy name=%s namespace=%s" % (self.deployment_name, self.deployment_namespace))
            api.patch(name=self.deployment_name, namespace=self.deployment_namespace, body=body, pretty='true')
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment_status: %s\n" % e)

    def update_configmap(self, filename):
        api = self.client.resources.get(api_version="v1", kind="ConfigMap")
        configmap_manifest = {
            "data": {
                "path": filename
            }
        }
        try:
            api.patch(name=self.configmap_name, namespace=self.configmap_namespace, body=configmap_manifest)
        except ApiException as e:
            print("Exception when calling v1->update_configmap: %s\n" % e)

    def watch_and_update_pmml_filepath(self):
        consumer = KafkaConsumer(self.kafka_topic_name, group_id='pmml', bootstrap_servers=self.kafka_bootstrap_servers)
        print("Watching topic %s for any new messages.." % self.kafka_topic_name)
        for msg in consumer:
            print("updating pmml file name to %s" % (msg.value.decode('UTF-8')))
            self.update_configmap(filename=msg.value.decode('UTF-8'))
            self.restart_deployment()
            consumer.commit()
