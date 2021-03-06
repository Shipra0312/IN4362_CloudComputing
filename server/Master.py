import boto3
import socket
import time
import threading
from server.Worker import Worker
from queue import Queue


class Master:
    ec2 = boto3.resource('ec2')

    def __init__(self):
        self.user_count = 0

        running_instances = list(self.ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]))
        self.available_instances = Queue()
        [self.available_instances.put(x.public_ip_address) for x in running_instances]
        print(list(self.available_instances.queue))

        self.ports = Queue()
        [self.ports.put(x) for x in range(8081, 8099)]

    def get_instance(self):
        if self.available_instances.empty():
            self.user_count = self.user_count + 1
            return None
        instance_ip = self.available_instances.get()
        self.user_count = self.user_count + 1
        return instance_ip

    def free_instance(self, instance_ip, port):
        if not(instance_ip == "None"):
            self.available_instances.put(instance_ip)
        self.user_count = self.user_count - 1
        self.ports.put(int(port))


def start_listening(worker):
    worker.start_listening()


def communication(master):
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('127.0.0.1', 8080))
    serv.listen(5)
    print("Master listening on port 8080")
    while True:
        print(master.user_count)
        print("Master waiting to accept")
        conn, addr = serv.accept()
        while True:
            data = conn.recv(128)
            msg = str(data.decode("utf-8")).split("_")
            print(f"Master msg: {msg}")
            if msg[0] == "free":
                master.free_instance(msg[1], msg[2])
                break
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
    #f = open("results/elasticityresults.txt", "a")
    while True:
        time.sleep(2)
        total_instance_amount = len(list(master.ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}])))
        running_instance_amount = len(list(master.ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running']}])))
        #f.write(f"{total_instance_amount},{running_instance_amount},{master.user_count}\n")
        #f.flush()
        #print(f"{total_instance_amount},{running_instance_amount},{master.user_count}")
        if running_instance_amount - master.user_count < 6:
            worker = Worker(None, None)
            start_instance_thread = threading.Thread(target=start_instance, args=(worker, master))
            start_instance_thread.start()
        elif running_instance_amount - master.user_count > 8:
            worker = Worker(None, None)
            stop_instance_thread = threading.Thread(target=stop_instance, args=(worker, master))
            stop_instance_thread.start()
        elif total_instance_amount - master.user_count < 6:
            worker = Worker(None, None)
            new_instance_thread = threading.Thread(target=create_instance, args=(worker, master))
            new_instance_thread.start()
        elif total_instance_amount - master.user_count > 10:
            worker = Worker(None, None)
            terminate_instance_thread = threading.Thread(target=terminate_instance, args=(worker, master))
            terminate_instance_thread.start()


def create_instance(worker, master):
    print("Creating new instance")
    master.available_instances.put(worker.create_instance())


def terminate_instance(worker, master):
    if master.available_instances.empty():
        return
    instance_ip = master.available_instances.get()
    print(f"Terminating instance: {instance_ip}")
    worker.terminate_instance(instance_ip)


def start_instance(worker, master):
    print("Starting instance")
    master.available_instances.put(worker.start_instance())


def stop_instance(worker, master):
    if master.available_instances.empty():
        return
    print("Stopping instance")
    instance_ip = master.available_instances.get()
    worker.stop_instance(instance_ip)


def main():
    master = Master()
    comm_thread = threading.Thread(target=communication, args=(master,))
    comm_thread.start()
    #mon_thread = threading.Thread(target=monitor, args=(master,))
    #mon_thread.start()


main()
