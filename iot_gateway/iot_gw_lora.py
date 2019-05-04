"""

file: iot_gw_lora.py

description: python simulation of a lora gateway


"""

from socketserver import *

class UDPHandler(BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(self.get_dev_addr(data), "toggle:", self.get_toggle(data))
        socket.sendto(b'GOTZIT', self.client_address)

    def get_dev_addr(self, data):
        field = str(data).split()[1][3:]
        return field

    def get_toggle(self,data):
        return str(data).split()[4][5:7]

if __name__ == '__main__':
    HOST, PORT = "localhost", 4280
    with UDPServer((HOST,PORT),UDPHandler) as server:
        ip,port = server.server_address
        print("Server running on port", port)
        server.serve_forever()