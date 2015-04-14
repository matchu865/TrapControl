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
		self.new = True

	def connectionMade(self):
		print "connectionMade"
				
	def connectionLost(self, reason):
		print "connectionLost " 
		if self.account in self.users:
			del self.users[self.account]	#removing user instance
		elif self.account in self.traps:
			del self.traps[self.account]
		print "User removed"

	def lineReceived(self, line):
		print "lineReceived: " + line
		self.handle_INPUT(line)

	#initial handler that parses xml to an orderedDict
	def handle_INPUT(self, data):
		
		xmldata = xmltodict.parse(data)
		if 'user' in xmldata.keys():
			print "Handling User Request"
			self.userResponse(xmldata)
		elif 'trap' in xmldata.keys():
			print "Handling Trap Request"
			self.trapResponse(xmldata)
		else:
			self.sendLine("Illegal Request: 0")	

	#Respond to request from User
	def userResponse(self, msg):
		print msg['user']['account']
		#check to see if acct. already exists
		if msg['user']['account'] in self.users:
			if msg['user']['request'] == 'THROW':
				self.sendTrapResponse('THROW',msg['user']['trap'], msg['user']['target'])

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
			pass
			##process request
		else: #new user
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

	def sendUsrResponse(self, response, trap, name, account, numTargets):
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


