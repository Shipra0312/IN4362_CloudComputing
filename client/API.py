import socket
import paramiko


def fit_predict(classifier, train_x, train_y, test_x):
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_port = get_port(master)

    worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    instance_ip = get_instance(worker, worker_port)
    key = paramiko.RSAKey.from_private_key_file("CC.pem")

    instance_ssh = paramiko.SSHClient()
    instance_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    instance_ssh.connect(hostname=instance_ip, username="ubuntu", pkey=key)

    code = open("instance_code.txt").read()
    code = code.replace("classifier", classifier).replace("train_x", str(train_x)) \
        .replace("train_y", str(train_y)).replace("test_x", str(test_x))
    stdin, stdout, stderr = instance_ssh.exec_command(f"rm -f test.py;printf {code} >>test.py;python3 test.py")
    stdout.channel.recv_exit_status()
    print(stdout.read().decode("utf-8"))
    print(stderr.read().decode("utf-8"))

    free_instance(worker, instance_ip, worker_port)


def get_port(master):
    master.connect(('127.0.0.1', 8080))
    master.send(b'get_worker')
    port = int(master.recv(128).decode("utf-8"))
    print(f"Worker port obtained: {port}")
    return port


def get_instance(worker, port):
    worker.connect(('127.0.0.1', port))
    worker.send(b'get_instance')
    instance_ip = worker.recv(128).decode("utf-8")
    print(f"Instance IP obtained: {instance_ip}")
    return instance_ip


def free_instance(worker, instance_ip, port):
    print("Releasing instance")
    free = f"free_{instance_ip}_{port}".encode("utf-8")
    worker.send(free)
    worker.close()
    print("Client closed")
