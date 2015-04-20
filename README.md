# TrapControl
# Android Client (User), Rasberry Pi Client (Trap), Python Server (AWS?)


Messaging Protocol

Android Client -> Server
####################################
# Create Account
# Connect to trap (optional?)
# Send Target Request
# Send info upon failed target ()
# Request Account Info

<user>
    <name></name>
    <account></account>
    <request></request>
    <trap></trap>
    <target></target>
</user>

name: contains name of user ex. "John Smith"
account: contains user's account number (must be unique)
request:    "THROW" -> request to launch target
            "FAIL" -> report a fail of the target
            "INFO" -> request acct info
            "PAY" -> requests acct. be reset (may not be implemented) 
trap: trap number client is requesting commmunication from
target: "H" -> high trap "L" -> low trap "P" -> Pair



Server -> Android Client
####################################
# Accept/Deny Account - Check Acct# doesn’t exist  
# Accept/Deny Connection to Machine
# Confirm Target Thrown
# Server User Usage Info

<userServer>
    <response></response>
    <trap></trap>
    <name></name>
    <account></account>
    <numTargets></numTargets>
</userServer>

response:   "ACCEPT" -> accept client upon connection or acct. creation
            "SUCCESS" -> standard response, serves all fields(trap can be NULL)
            "FAIL" -> trap requested is busy, offline, not ready 
trap: trap number client is requesting commmunication from
name: user's name
Account: user's acct. number (unique)
numTargets: returns number of targets user has thrown


####################################
Server -> Trap Client
# Request Target Thrown
# Query Status (Ready/Busy, Inventory)


<trapServer>
    <account></account>
    <command></command>
    <tnum></tnum>
    <target></target>
</trapServer>

command:    "THROW" -> request to throw target
            "ACCEPT" -> response to adding trap client **MAY REMOVE**
            "SHUTDOWN" -> request to take trapclient online
tnum: trap number
target: "H" -> high trap "L" -> low trap "P" -> Pair



Trap Client -> Server
####################################
# Go Online (Send signal to be added)
# Confirm Target Thrown
# Reply Ready/Busy (Includes Inventory Info)

<trap>
    <account></account>
    <status></status>
    <response></response>
    <hInv></hInv>
    <lInv></lInv>
</trap>

tnum: trap number
status: "H" -> high trap "L" -> low trap "P" -> Pair "R" -> Ready
response:   "SUCCESS" -> trap successfully thrown
            "FAIL" -> problem with trap
hInv: high trap inventory
lInv: low trap inventory







