import boto3
import socket
import time
import paramiko


class Master:
    IMAGE_ID = 'ami-0eb89db7593b5d434'
    ec2 = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')

    def __init__(self):
        self.key = paramiko.RSAKey.from_private_key_file("CC.pem")
        running_instances = list(self.ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]))
        self.available_instances = list(map(lambda x: x.public_ip_address, running_instances))
        #self.available_instances = []

    def get_instance(self):
        if len(self.available_instances) == 0:
            return self.start_instance()
        instance_ip = self.available_instances[0]
        self.available_instances.remove(instance_ip)
        return instance_ip

    def start_instance(self):
        stopped_instances = list(self.ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]))

        if len(stopped_instances) == 0:
            return self.create_instance()

        new_instance = stopped_instances[0]
        self.ec2_client.start_instances(InstanceIds=[new_instance.id], DryRun=False)
        new_instance.wait_until_running()
        return new_instance.public_ip_address

    def create_instance(self):
        new_instance = self.ec2.create_instances(ImageId=self.IMAGE_ID, InstanceType='t2.micro', MinCount=1, MaxCount=1,
                    KeyName='CC', SecurityGroups=['launch-wizard-2'],
                    IamInstanceProfile={'Name': 'SSM'})
        new_instance[0].wait_until_running()
        time.sleep(60)
        new_instance[0].reload()
        self.setup_instance(new_instance[0].public_ip_address)
        return new_instance[0].public_ip_address

    def stop_instance(self, instance_ip):
        filters = [{
            'Name': 'ip-address',
            'Values': [instance_ip],
        }]
        results = self.ec2_client.describe_instances(Filters=filters)
        instance_id = results['Reservations'][0]['Instances'][0]['InstanceId']
        self.ec2_client.stop_instances(InstanceIds=[instance_id], DryRun=False)
        return

    def free_instance(self, instance_ip):
        self.available_instances.append(instance_ip)

    def setup_instance(self, instance_ip):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print("Setting up instance")
        client.connect(hostname=instance_ip, username="ubuntu", pkey=self.key)
        stdin, stdout, stderr = client.exec_command("sudo apt install -y python3-pip")
        stdout.channel.recv_exit_status()
        print(f"Installed pip on {instance_ip}")
        stdin, stdout, stderr = client.exec_command("pip3 install sklearn")
        stdout.channel.recv_exit_status()
        print(f"Installed sklearn on {instance_ip}")
        return


def main():
    master = Master()

    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('127.0.0.1', 8080))
    serv.listen(5)
    print("Listening on port 8080")

    while True:
        print("Waiting to accept")
        conn, addr = serv.accept()
        while True:
            data = conn.recv(128)
            print(str(data.decode("utf-8")))
            msg = str(data.decode("utf-8")).split("_")
            if msg[0] == "free":
                master.free_instance(msg[1])
                break
            elif msg[0] == "get":
                instance_ip = master.get_instance().encode("utf-8")
                conn.send(instance_ip)


main()
