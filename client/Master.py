import boto3
import socket
import time
import threading
from client.Worker import Worker
from queue import Queue


class Master:
    ec2 = boto3.resource('ec2')

    def __init__(self):
        self.user_count = 0

        running_instances = list(self.ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]))
        self.available_instances = list(map(lambda x: x.public_ip_address, running_instances))
        #self.available_instances = []

        self.ports = Queue()
        [self.ports.put(x) for x in range(8081, 8099)]

    def get_instance(self):
        self.user_count = self.user_count + 1
        if len(self.available_instances) == 0:
            return None
        instance_ip = self.available_instances[0]
        self.available_instances.remove(instance_ip)
        return instance_ip

    def free_instance(self, instance_ip, port):
        self.available_instances.append(instance_ip)
        self.ports.put(port)
        self.user_count = self.user_count - 1


def start_listening(worker):
    worker.start_listening()


def communication(master):
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('127.0.0.1', 8080))
    serv.listen(5)
    print("Master listening on port 8080")
    while True:
        print("Master waiting to accept")
        conn, addr = serv.accept()
        while True:
            data = conn.recv(128)
            msg = str(data.decode("utf-8")).split("_")
            print(f"Master msg: {msg}")
            if msg[0] == "free":
                master.free_instance(msg[1], msg[2])
            elif msg[0] == "get":
                port = master.ports.get()
                conn.send(str(port).encode("utf-8"))
                conn.close()
                worker = Worker(port, master.get_instance())
                thread1 = threading.Thread(target=start_listening, args=(worker,))
                thread1.start()
                break
            else:
                break


def monitor(master):
    while True:
        active_instance_amount = len(list(master.ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}])))
        time.sleep(2)
        if active_instance_amount < 2:
            worker = Worker(None, None)
            new_instance_thread = threading.Thread(target=create_instance, args=(worker, master))
            new_instance_thread.start()
        elif active_instance_amount - master.user_count < 2:
            worker = Worker(None, None)
            new_instance_thread = threading.Thread(target=create_instance, args=(worker, master))
            new_instance_thread.start()


def create_instance(worker, master):
    print("Creating new instance")
    master.available_instances.append(worker.create_instance())


def main():
    master = Master()
    comm_thread = threading.Thread(target=communication, args=(master,))
    comm_thread.start()
    mon_thread = threading.Thread(target=monitor, args=(master,))
    mon_thread.start()


main()
