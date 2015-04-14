
#!/usr/bin/env python 

#import RPi.GPIO as GPIO  #GPIO Library for rasberry pi
import sys
import time
import socket
import xmltodict

TCP_IP = '127.0.0.1'
TCP_PORT = 8000

BUFFER_SIZE = 1024


class TrapClient:
	def __init__(self, tnum):
		self.hInv = 250
		self.lInv = 250
		self.status = 'R'
		self.tnum = tnum
		self.sock = None
		self.timeH = time.time()
		self.timeL
		print "finished init"


	def connect(self):
		print TCP_IP,TCP_PORT
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.connect((TCP_IP, TCP_PORT))

		#Send welcome message
		self.sendMessage(self.tnum, self.status, 'R', self.hInv, self.lInv)		
		print "finished connect"

	def run(self):
		while 1:
			print "blocking on data"
			data = self.sock.recv(BUFFER_SIZE)
			xmldata = xmltodict.parse(data)
			if xmldata['trapServer']['command'] == 'THROW':
					#set status
					#reply SUCCESS


				pass
			else:
				pass



	#Sends reply to server over socket
	def sendMessage(self, tnum, status, response, hInv, lInv):
		msg = { 'trap' :{
			'tnum' : tnum,
			'status' : status,
			'response' : response,
			'hInv' : hInv,
			'lInv' : lInv,
		}}
		self.sock.send(xmltodict.unparse(msg).encode("utf-8") + "\r\n")




def main():
	try:
		trap = TrapClient(sys.argv[1])
		trap.connect()
		trap.run()



	except Exception as ex:
		print ex.message
		return 1
	else:
		return 0	
		
if __name__ == '__main__':
	main()

