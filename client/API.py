import socket
import paramiko
import math
import numpy as np


def fit_predict(classifier, x_train, y_train, x_test):
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_port = get_port(master)

    worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    instance_ip = get_instance(worker, worker_port)
    key = paramiko.RSAKey.from_private_key_file("CC.pem")

    instance_ssh = paramiko.SSHClient()
    instance_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    instance_ssh.connect(hostname=instance_ip, username="ubuntu", pkey=key)

    write_x_data(instance_ssh, x_train, "x_train.txt")
    write_y_data(instance_ssh, y_train, "y_train.txt")
    write_x_data(instance_ssh, x_test, "x_test.txt")

    code = open("instance_code.txt").read()
    code = code.replace("classifier", classifier)
    #stdin, stdout, stderr = instance_ssh.exec_command(f"echo $(cat x_test.txt)")
    stdin, stdout, stderr = instance_ssh.exec_command(f"rm -f test.py;printf {code} >>test.py;python3 test.py")
    stdout.channel.recv_exit_status()
    output = stdout.read().decode("utf-8")
    error = stderr.read().decode("utf-8")
    print(output)
    print(error)

    free_instance(worker, instance_ip, worker_port)
    return output


def calculate_step_size(n_features):
    max_size = 5000
    return int(math.ceil(max_size / n_features))


def write_x_data(instance_ssh, data, filename):
    instance_ssh.exec_command(f"rm -f {filename}")

    step_size = calculate_step_size(data.shape[1])
    windows = int(math.ceil(len(data) / step_size))
    for i in range(windows):
        index = np.minimum((i + 1) * step_size, len(data) + 1)
        if i == windows - 1:
            string = '\\n'.join(' '.join(str(cell) for cell in row) for row in data[i * step_size:]) + "\\n"
        else:
            string = '\\n'.join(' '.join(str(cell) for cell in row) for row in data[i * step_size:index]) + "\\n"
        stdin, stdout, stderr = instance_ssh.exec_command(f"printf -- \"{string}\"  >>{filename}")
        stdout.channel.recv_exit_status()
    return


def write_y_data(instance_ssh, data, filename):
    instance_ssh.exec_command(f"rm -f {filename}")

    step_size = calculate_step_size(data.shape[0])
    windows = int(math.ceil(len(data) / step_size))
    for i in range(windows):
        index = np.minimum((i + 1) * step_size, len(data) + 1)
        if i == windows - 1:
            string = '\\n'.join(str(row) for row in data[i * step_size:]) + "\\n"
        else:
            string = '\\n'.join(str(row) for row in data[i * step_size:index]) + "\\n"
        stdin, stdout, stderr = instance_ssh.exec_command(f"printf \"{string}\"  >>{filename}")
        stdout.channel.recv_exit_status()
    return


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
