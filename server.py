from socket import *

from code_completion_lib.code_completion import CodeCompletion


class Server:
    completion = None
    HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'

    def __init__(self, ip, port, base_name):
        print(f"SERVER IP: {ip}\nSERVER PORT: {port}\n")

        self.completion = CodeCompletion()
        self.base_name = base_name
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(100)

    def sender(self, user, text):
        user.send(self.HDRS.encode('latin-1') + text.encode('latin-1'))

    def start_server(self):
        while True:
            user, addr = self.server.accept()
            print(f"CLIENT CONNECTED:\n\tIP: {addr[0]}\n\tPORT: {addr[1]}")
            self.listen(user)

    def listen(self, user):
        is_work = True

        while is_work:
            try:
                data = user.recv(1024)

            except Exception as e:
                data = ""
                is_work = False

            if len(data) > 0:
                msg = data.decode('latin-1')

                if msg == 'disconnect':
                    self.sender(user, "YOU ARE DISCONNECTED!")
                    user.close()
                    is_work = False
                else:
                    data = msg.split("\n")[0].replace(' HTTP', '').replace("[", "").replace("]", "").split("/")
                    var = data[1].replace(' ', '')
                    imports_lib = data[2].split(', ')
                    if var == var.replace("=", ""):
                        answer = f"Unable to get method completion | {self.completion.get_variable_completion(var, imports_lib)}"
                    else:
                        full_imports = data[3].split(', ')
                        print(f"full_imports = {full_imports}")
                        var = var.replace("=", "")
                        answer = self.completion.get_function_completion(var, imports_lib, full_imports)

                    print(f"var = {var}")
                    print(f"imports_lib = {imports_lib}")
                    print(f"answer = {answer}")
                    self.sender(user, f"{answer}")
                    user.close()
                    is_work = False
                    print("CLIENT DISCONECTED")
            else:
                print("CLIENT DISCONECTED")


Server('localhost', 7000, 'data.db').start_server()
