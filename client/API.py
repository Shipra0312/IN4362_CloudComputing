import boto3
import time
import socket


def fit_predict(classifier, train_x, train_y, test_x):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8080))
    client.send(b'get_instance')
    instance_id = client.recv(4096).decode("utf-8")
    print(instance_id)

    ssm_client = boto3.client('ssm')
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands': [
                'echo fit and predict'
            ]
        }
    )
    time.sleep(1)
    command_id = response['Command']['CommandId']
    output = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id,
    )
    print(output['StandardOutputContent'])

    print("Releasing instance")
    free = f"free_{instance_id}".encode("utf-8")
    client.send(free)
    print("Client closed")

