
#!/usr/bin/env python 

#import RPi.GPIO as GPIO  #GPIO Library for rasberry pi
import sys
import time
import socket
import xmltodict

TCP_IP = '127.0.0.1'
TCP_PORT = 8000

BUFFER_SIZE = 1024
DELAY = 2

class TrapClient:
	def __init__(self, tnum):
		self.hInv = 250
		self.lInv = 250
		self.status = 'R'
		self.tnum = tnum
		self.sock = None
		self.timeH = time.time()
		self.timeL = self.timeH
		print "finished init"


	def connect(self):
		print TCP_IP,TCP_PORT
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.connect((TCP_IP, TCP_PORT))

		#Send welcome message
		self.sendMessage(self.tnum, self.status, 'R', self.hInv, self.lInv)		
		print "finished connect"

	def run(self):
		print "running"
		while 1:
			print "blocking on data"
			data = self.sock.recv(BUFFER_SIZE)
			xmldata = xmltodict.parse(data)
			hStat = ((time.time() - self.timeH) > DELAY)
			lStat = ((time.time() - self.timeL) > DELAY)

			"""Handle 'THROW' commands. Could reduce redundancy but for prototype unneccessary"""
			if xmldata['trapServer']['command'] == 'THROW':
				#Pair				
				if xmldata['trapServer']['target'] == 'P':
					if not hStat or not lStat or self.hInv <= 0 or self.lInv <=0:
						#FAIL
						self.sendMessage(self.tnum, 'P', 'FAIL', self.hInv, self.lInv)
					else:
						self.hInv -= 1
						self.lInv -= 1
						self.timeH = time.time()
						self.timeL = self.timeH
						self.sendMessage(self.tnum, 'P', 'SUCCESS', self.hInv, self.lInv)
				#High House 
				elif xmldata['trapServer']['target'] == 'H' or self.hInv <=0:
					if not hStat:
						self.sendMessage(self.tnum, 'H', 'FAIL', self.hInv, self.lInv)
					else:
						self.hInv -= 1
						self.timeH = time.time()
						self.sendMessage(self.tnum, 'H', 'SUCCESS', self.hInv, self.lInv)
				#Low House
				elif xmldata['trapServer']['target'] == 'L' or self.lInv <=0:
					if not lStat:
						self.sendMessage(self.tnum, 'L', 'FAIL', self.hInv, self.lInv)
					else:
						self.lInv -= 1
						self.timeL = time.time()
						self.sendMessage(self.tnum, 'L', 'SUCCESS', self.hInv, self.lInv)
				else:
					print "ERROR: " + xmldata['trapServer']['target']
					self.sendMessage(self.tnum, 'P', 'FAIL', self.hInv, self.lInv)
			elif xmldata['trapServer']['command'] == 'SHUTDOWN':
				print "Shutting Down Trap"
				self.sock.close()
			else:
				print "Received Illegal message. No action"



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
		print "EXCEPTION: " + ex.message
		return 1
	else:
		return 0	
		
if __name__ == '__main__':
	main()

