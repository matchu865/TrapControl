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

	def connectionMade(self):
		print "connectionMade"
				
	def connectionLost(self, reason):
		print "connectionLost " 
		#if self.name in self.users:
		#	del self.users[self.name]	#removing user instance
		pass

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
			##process request
			pass
		else: #new user
			self.addAccount(msg)

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
		self.numTargets = 0		#new accounts will start with 0
		self.users[self.account] = self
		#Need to add message
		print "Added: " + self.name + self.account
	
	#Adds a trap to the server
	def addTrap(self, msg):
		self.tnum = msg['trap']['tnum']
		self.status = msg['trap']['status']
		self.hInv = msg['trap']['hInv']
		self.lInv = msg['trap']['lInv']
		self.traps[tnum] = self
		print "Added: " + self.tnum 


		

		


class ControlSystemFactory(Factory):
	def __init__(self):
		self.users = {} #maps usernames to instances of Server
		self.traps = {} #maps traps to instances of ControlSystem

	def buildProtocol(self, addr):
		return ControlSystem(self.users, self.traps)


if __name__ == '__main__':
    reactor.listenTCP(8000, ControlSystemFactory())
    reactor.run()


