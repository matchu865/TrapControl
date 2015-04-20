
#!/usr/bin/env python 

import RPi.GPIO as GPIO  #GPIO Library for rasberry pi
import sys
import time
import socket
import xmltodict
from threading import Thread

TCP_IP = '54.149.14.43'
TCP_PORT = 8000
PIN1 = 3
PIN2 = 5

BUFFER_SIZE = 1024
DELAY = 4

class TrapClient:
	def __init__(self, tnum):

		#configure gpio
		GPIO.setmode(GPIO.BCM)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(PIN1,GPIO.OUT,initial = 1)
		GPIO.setup(PIN2,GPIO.OUT,initial = 1)

		self.hInv = 250
		self.lInv = 250
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
		self.sendMessage(0, 'R', 'SUCCESS', self.hInv, self.lInv)		
		print "finished connect"

	def run(self):
		print "running"
		while 1:
			print "blocking on data"
			data = self.sock.recv(BUFFER_SIZE)
			print "line received: " + data
			xmldata = xmltodict.parse(data)
			hStat = ((time.time() - self.timeH) > DELAY)
			lStat = ((time.time() - self.timeL) > DELAY)

			"""Handle 'THROW' commands. Could reduce redundancy but for prototype unneccessary"""
			if xmldata['trapServer']['command'] == 'THROW':
				#Pair				
				if xmldata['trapServer']['target'] == 'P':
					if not hStat or not lStat or self.hInv <= 0 or self.lInv <=0:
						#FAIL
						self.sendMessage(xmldata['trapServer']['account'], 'P', 'FAIL', self.hInv, self.lInv)
					else:
						self.hInv -= 1
						self.lInv -= 1
						self.timeH = time.time()
						self.timeL = self.timeH
						self.sendMessage(xmldata['trapServer']['account'], 'P', 'SUCCESS', self.hInv, self.lInv)

						#thread and wait
						t = Thread(target = gpioDelay, args(True,True))
						t.start()
				#High House 
				elif xmldata['trapServer']['target'] == 'H' or self.hInv <=0:
					if not hStat:
						self.sendMessage(xmldata['trapServer']['account'], 'H', 'FAIL', self.hInv, self.lInv)
					else:
						self.hInv -= 1
						self.timeH = time.time()
						self.sendMessage(xmldata['trapServer']['account'], 'H', 'SUCCESS', self.hInv, self.lInv)

						t = Thread(target = gpioDelay, args(True,False))
						t.start()
				#Low House
				elif xmldata['trapServer']['target'] == 'L' or self.lInv <=0:
					if not lStat:
						self.sendMessage(xmldata['trapServer']['account'], 'L', 'FAIL', self.hInv, self.lInv)
					else:
						self.lInv -= 1
						self.timeL = time.time()
						self.sendMessage(xmldata['trapServer']['account'], 'L', 'SUCCESS', self.hInv, self.lInv)

						t = Thread(target = gpioDelay, args(False,True))
						t.start()
				else:
					print "ERROR: " + xmldata['trapServer']['target']
					self.sendMessage(xmldata['trapServer']['account'], 'P', 'FAIL', self.hInv, self.lInv)
			elif xmldata['trapServer']['command'] == 'SHUTDOWN':
				print "Shutting Down Trap"
				self.sock.close()
			else:
				print "Received Illegal message. No action"



	#Sends reply to server over socket
	def sendMessage(self, account, status, response, hInv, lInv):
		msg = { 'trap' :{
			'tnum' : self.tnum,
			'account' : account,
			'status' : status,
			'response' : response,
			'hInv' : hInv,
			'lInv' : lInv,
		}}
		self.sock.send(xmltodict.unparse(msg).encode("utf-8") + "\r\n")

	def setGPIO(self, hightrap, lowtrap):
		GPIO.output(PIN1,hightrap)
		GPIO.output(PIN2,lowtrap)
		time.sleep(DELAY)
		if not hightrap:
			GPIO.output(PIN1, True)
		if not lowtrap:
			GPIO.output(PIN2, True)



def main():
	try:
		trap = TrapClient(sys.argv[1])
		trap.connect()
		trap.run()



	except Exception as ex:
		print "EXCEPTION: " + str(ex)
		return 1
	else:
		return 0	
		
if __name__ == '__main__':
	main()

