#!/usr/bin/env python
import xmltodict

class TestClass():
	a = 20
	def __init__(self):
		self.i = 10
		z = 15

	def otherFunc(self):
		self.j = 15
		x = 27

a = TestClass()
print "a", a.a
print "i", a.i
print "z", a.z
print "j", a.j
print "x", a.x


