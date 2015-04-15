#!/usr/bin/env python
import xmltodict
from cStringIO import StringIO

from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import logging


### Protocol Implementation
class ControlSystem(LineReceiver):

	def __init__(self, users, traps):
		self.users = users
		self.traps = traps
		self.account = None #users & traps can have the same number
		self.tnum = None
		self.new = True

	def connectionMade(self):
		print "connectionMade"
				
	def connectionLost(self, reason):
		print "connectionLost " 
		if self.users.get(self.account):
			del self.users[self.account]	#removing user instance
		elif self.traps.get(self.tnum):
			del self.traps[self.tnum]
		print "User removed"

	def lineReceived(self, line):
		print "lineReceived: " + line
		self.handle_INPUT(line)

	#initial handler that parses xml to an orderedDict
	def handle_INPUT(self, data):
		xmldata = None
		try:	
			xmldata = xmltodict.parse(data)
			if xmldata.get('user'):
				print "Handling User Request"
				self.userResponse(xmldata)
			elif xmldata.get('trap'):
				print "Handling Trap Request"
				self.trapResponse(xmldata)
			else:
				self.sendLine("Illegal Request: 0")	
		except Exception as ex:
			print "EXCEPTION: " + str(ex) 
			self.sendLine("Illegal Request: " + str(ex))


	#Respond to request from User
	def userResponse(self, msg):
		print msg['user']['account']
		#check to see if acct. already exists
		if msg['user']['account'] in self.users:
			if msg['user']['request'] == 'THROW':
				self.sendTrapResponse('THROW',msg['user']['trap'], msg['user']['target'])
			#allow user to credit for trap error not caught by trap response
			elif msg['user']['request'] == 'FAIL':
				if self.numTargets > 0: self.numTargets -= 1
				self.sendUsrResponse('SUCCESS', '', self.name, self.account, self.numTargets)
			elif msg['user']['request'] == 'INFO':
				self.sendUsrResponse('SUCCESS', '', self.name, self.account, self.numTargets)
			elif msg['user']['request'] == 'PAY':
				self.numTargets = 0 #user 'paid'
				#may change to prompt user to disconnect. Now a standard success response is sent
				self.sendUsrResponse('SUCCESS', '', self.name, self.account, self.numTargets)
			else:
				pass
		elif self.new: #new user
			self.addAccount(msg)
		else:
			self.sendLine("Account already exists")

	#Respond to request from Trap
	def trapResponse(self, msg):
		print msg['trap']['tnum']
		#check to see if acct. already exists
		if msg['trap']['tnum'] in self.traps:
			self.tnum = msg['trap']['tnum']
			account = msg['trap']['account']
			self.status = msg['trap']['status']
			self.hInv = msg['trap']['hInv']
			self.lInv = msg['trap']['lInv']
			response = msg['trap']['response']
			if response == 'SUCCESS':
				#increment user's numTargets
				if self.status == 'P':
					self.users[account].numTargets += 2
				else:
					self.users[account].numTargets += 1
			self.sendUsrResponse(response,self.tnum,'',account, self.users[account].numTargets)
		#new user
		else: 
			self.addTrap(msg)


	#Adds a user to the server so they can request targets		
	def addAccount(self, msg):
		self.account = msg['user']['account']
		self.name = msg['user']['name']
		self.numTargets = 0		#new accounts will start with 0 targets
		self.new = False
		self.users[self.account] = self
		#Need to add message
		print "Added user: " + self.name + " " + self.account
	
	#Adds a trap to the server
	def addTrap(self, msg):
		self.tnum = msg['trap']['tnum']
		self.status = msg['trap']['status']
		self.hInv = msg['trap']['hInv']
		self.lInv = msg['trap']['lInv']
		self.new = False
		self.traps[self.tnum] = self
		print "Added trap: " + self.tnum

	def sendUsrResponse(self, response, trap,name, account, numTargets):
		mydict = {'userServer': {
			'response' : response ,
			'trap' : trap ,
			'name' : name ,
			'account' : account ,
			'numTargets' : numTargets,}}
		if self.users[account]:
			self.users[account].sendLine(xmltodict.unparse(mydict).encode("utf-8"))
		else:
			##USER Does Not Exist Recursively send error message
			print "ERROR: sending user message"
			self.sendUsrResponse('ERROR',trap,self.name,self.account, self.numTargets)
		

	def sendTrapResponse(self, command, tnum, target):
		print "contacting trap: " + command, tnum, target
		if self.traps[tnum] : 
			mydict = {'trapServer' : {
			'command' : command,
			'tnum' : tnum,
			'target' : target,
			'account' : self.account
			}}
			self.traps[tnum].sendLine(xmltodict.unparse(mydict).encode("utf-8"))
		else: 
			sendUsrResponse('BUSY', tnum, self.name, self.account, '0')







class ControlSystemFactory(Factory):
	def __init__(self):
		self.users = {} #maps usernames to instances of Server
		self.traps = {} #maps traps to instances of ControlSystem

	def buildProtocol(self, addr):
		return ControlSystem(self.users, self.traps)


if __name__ == '__main__':
    reactor.listenTCP(8000, ControlSystemFactory())
    reactor.run()


