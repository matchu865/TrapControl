import xmltodict


# mydict = {'userServer': {
# 			'response' : 'SUCCESS',
# 			'trap' : '2',
# 			'name' : 'Matthew',
# 			'account' : '124' ,
# 			'numTargets' : '250',
# 		}	
# 	}
# print xmltodict.unparse(mydict)
# print xmltodict.unparse(mydict, pretty=True)

def sendUsrResponse( response, trap, name, account, numTargets):
	mydict = {'userServer': {
		'response' : response ,
		'trap' : trap ,
		'name' : name ,
		'account' : account ,
		'numTargets' : numTargets,}}
	print xmltodict.unparse(mydict)

sendUsrResponse('SUCCESS', 2, 'Matthew', 123, 250)




# <userServer>
#     <response></response>
#     <trap></trap>
#     <name></name>
#     <account></account>
#     <numTargets></numTargets>
# </userServer>