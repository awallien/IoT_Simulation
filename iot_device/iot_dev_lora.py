"""
file: iot_dev_lora.py

description: python simulation of an IoT Device under the
    LoRa protocol, class A devices

"""

import socket
import threading
import time
import sys

"""
All class here are made up payload data, especially the toggle info
"""
class FHDRPayload:
    dev_addr = ""
    fctrl = bytes([1,1,1,1,0,0,0,0])
    fcnt = b'1'
    fopts = b'0'

    def __init__(self, dev_addr, toggle):
        self.dev_addr = dev_addr
        self.fopts = bytes([toggle])

    def info(self) -> list:
        if self.dev_addr == "":
            raise Exception("Error: Invalid Device Address ", self.dev_addr)
        return [self.dev_addr, self.fctrl, self.fcnt, self.fopts]


class MACPayload:
    fport = bytes([11])
    frm_payload = b'0'

    def __init__(self, fhdrpayload):
        self.fhdr_payload = fhdrpayload

    def info(self) -> list:
        if self.fhdr_payload is None:
            raise Exception("Error: FHDR Payload is empty")
        return [self.fhdr_payload.info(), self.fport, self.frm_payload]


class PHYPayload:
    mhdr = bytes([0,0,0,0,0,0,0,1])
    mic = bytes([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    def __init__(self, mac):
        self.mac_payload = mac

    def info(self) -> list:
        if self.mac_payload is None:
            raise Exception("Error: MAC Payload is empty")
        return [self.mhdr, self.mac_payload.info(), self.mic]


class LoRaDevice:
    preamble = bytes([0, 0, 0, 0, 0, 0, 0, 0])
    phdr = bytes((0, 1, 1, 0, 1, 1, 1, 0))
    phdr_CRC = bytes(127)
    CRC = bytes(127)

    def __init__(self, phyPayload):
        self.phy_payload = phyPayload

    def info(self) -> list:
        if self.phy_payload is None:
            raise Exception("Error: PHY Payload cannot be empty")
        return [self.preamble, self.phdr, self.phdr_CRC, self.phy_payload.info(), self.CRC]


class LoRaTransmitter:

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = port
        self.recv_start = False

    def send(self, msg):
        ip_port = ("localhost", self.port)
        self.sock.sendto(bytes(msg,"utf-8"), ip_port)

        if not self.recv_start:
            threading.Thread(target=self.recv()).start()

    def recv(self):
        print("Data received from GW: ",self.sock.recvfrom(100))


class Toggle:

    def __init__(self):
        self.on = False

    def get(self):
        return self.on

    def toggle(self):
        if self.on:
            self.on = False
        else:
            self.on = True


def user_toggle(toggle):
    while True:
        input()
        toggle.toggle()
        print("Toggle set: ", toggle.get())


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: python3.7 iot_dev_lora.py device-address")
        sys.exit(1)

    dev_addr = sys.argv[1]

    sock = LoRaTransmitter(4280)

    toggle = Toggle()
    toggle_t = threading.Thread(target=user_toggle, args=(toggle,))
    toggle_t.start()

    while True:
        time.sleep(1)
        device = LoRaDevice(PHYPayload(MACPayload(FHDRPayload(dev_addr,toggle.get()))))
        info = "".join(map(str,device.info()))
        print("[%s]: sending info to gateway: %s" % (dev_addr,info))
        sock.send(info)
