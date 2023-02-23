import os, select, socket, sys, threading, time

import glob
from utils import *


def to_bytes(string):
	b = bytearray()
	b.extend(string.encode())
	return b

def to_string(bytes_obj):
	return bytes_obj.decode('ascii')


class ControlSocket:
	def __init__(self, phase):
		self.socket = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
		i = 0
		while i<15:
			i+=1
			try:
				self.socket.bind((socket.VMADDR_CID_HOST, glob.CONTROL_PORT))
			except:
				time.sleep(1)
			else:
				break
		if i>=15:
			eprint("ControlSocket.__init__: failed to bind socket, VM probably failed to boot")
		self.socket.settimeout(240) # Timeout for VM connection is 4min
		# (We wait both for the VM to boot and for WalT to start)
		self.socket.listen(1)
		self.phase = phase

	def initiate(self, backends=[], macs=[], usernames=[], passwords=[], images=[]):
		log(DEBUG, "ControlSocket: waiting VM boot")
		try:
			self.conn, addr = self.socket.accept()
		except socket.timeout:
			eprint("ControlSocket.initiate: it seems like the VM failed to boot.")
		except:
			eprint("ControlSocket.initiate: unknown error occured when waiting for the VM")
		else:
			log(DEBUG, "ControlSocket: VM booted successfully")
			log(DEBUG, "ControlSocket: sending phase")
			self.send(str(self.phase))
			self.wait_confirm()
			
			if self.phase == 1:
				log(DEBUG, "ControlSocket: sending images")
				self.send_elems(images)
				if self.wait_confirm():
					# Sending the users to be added to the images
					# This will allow cowrie to connect (and will
					# allow brut force from a node to another)
					log(DEBUG, "ControlSocket: sending usernames")
					self.send_elems(usernames)
					self.wait_confirm()

					log(DEBUG, "ControlSocket: sending passwords")
					self.send_elems(passwords)
					self.wait_confirm()
					
					log(DEBUG, "ControlSocket: sending backends")
					self.send_elems(backends)
					self.wait_confirm()

					log(DEBUG, "ControlSocket: sending MACs")
					self.send_elems(macs)
					self.wait_confirm()
				else:
					eprint("ControlSocket.initiate: failed to download WalT images on the VM")
				ips = self.recv_elems()
				self.send_confirm()
				log(DEBUG, "ControlSocket: received ips: "+str(ips))
				return ips
			else:
				log(DEBUG, "ControlSocket: sending images")
				self.send_elems(images)
				self.wait_confirm()

				log(DEBUG, "ControlSocket: sending backends")
				self.send_elems(backends)
				self.wait_confirm(timeout=240) # Waiting 2 minutes for all the nodes to boot
				#log(DEBUG, "ControlSocket: walt nodes booted successfully")
			return None

	def send_confirm(self):
		self.send("1")

	def send_fail(self):
		self.send("0")

	def ask_reboot(self, backend):
		self.send("reboot:"+backend)
		return self.wait_confirm()

	def wait_confirm(self, timeout=30):
		res = self.recv(timeout=timeout)
		return res[0] == "1"

	def send(self, string):
		self.conn.send(to_bytes(string+"\n"))

	def recv(self, timeout=30):
		self.conn.settimeout(timeout)
		try:
			res = self.conn.recv(2048)
		except socket.timeout:
			eprint("ControlSocket.recv: reached timeout")
		except:
			eprint("ControlSocket.recv: an unknown error occured")
		else:
			if not res:
				eprint("ControlSocket.recv: Connection terminated")
			return to_string(res)

	def send_elems(self, elems, sep=" "):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem) + sep
		self.send(str_elems)

	def recv_elems(self, sep=" "):
		elems = self.recv().strip()
		if not elems:
			return []
		return elems.split(sep)

	def close(self):
		if conn is not None:
			self.conn.close()
		self.socket.close()


def main():
    socket = ControlSocket(1)
    socket.initiate(backends=[], usernames=[], passwords=[], images=[])

if __name__ == '__main__':
        main()