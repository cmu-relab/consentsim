'''
7/9/20
Simulation.py
'''
import OWLgenerator as ow
import numpy as np
import random
import time



class Simulation:
	
	def __init__(self, userTable, simScript, owlIRI):
		#contains which timestep program is in
		self.timeStep = 0

		self.simOnto = ow.OWLgenerator(owlIRI)

		#parse contingency table demoCols/Rows are col/row lables
		#users are the actual numbers of users data, userRrops are the calculated proportions users in each demographic category
		self.demoCols, self.demoRows, self.users, self.userProps = self.parseTable(userTable)

		self.currentUsers = self.users

		self.totalUsersAdded = self.users.sum()

		self.totalCollectionEvents = 0

		#adds users to the ontology
		for i in range(1, self.totalUsersAdded+1):
			newU = "U" + str(i)
			cName = newU + "initialConsent"
			self.simOnto.createNewClass("User", newU)

			self.simOnto.userConsent("D1", newU, "T0", "Recipient", cName)

			#create the consent for user. For do Dtype 1, time 0, R1. now, I'm just going to 

		#contains how often each data type is collected or accessed. Filled in parseScript
		self.collectFreqs = {}
		self.accessFreqs = {}

		#contains the numbers of the data collection for the last dc event for each data type
		#allows access to access the proper dataCollection log
		self.dcNumRange = {}

		#to track which users to withdraw consent, and how many to collect/access data from
		self.numUsersWithdrawn = 0

		self.initialPolicy = ("D1", "Recipient", "cr",)

		#parse script
		self.eventList = self.parseScript(simScript)

		self.name = simScript[:-3] + "owl"

	#parses the contingency table of the population into a numpy array
	def parseTable(self, tableTxt):
		#parse table here
		#read in line by line, add to list, convert to numpy
		#print to check table
		file = open(tableTxt, "r")
		tableList = None
		for line in file:
			splitLine = line.split("\t")
			stripped = line.split()

			if tableList == None:
				tableList = []
				stripped.insert(0, "demographics")
				tableList.append(stripped)
			else:
				tableList.append(stripped)

		table = np.array(tableList)
		cols = table[0,1:]
		rows = table[1:,0]
		users = table[1:, 1:].astype(int)

		props = users / users.sum()

		file.close()

		return cols, rows, users, props


	#parses the script for the simulation into a useful data structure
	def parseScript(self, simScriptTxt):
		file = open(simScriptTxt, "r")
		eventList = []

		# print("\n\n\nremember to uncomment events\n\n\n")
		for line in file:
			typeSplit = line.split(":")

			newEvent = None


			#new time interval
			if typeSplit[0].rstrip("\n") == "^":
				newEvent = Event()
				eventList.append(newEvent)
				# print("New Time step!")

			#policy change
			elif typeSplit[0] == "+":
				pcData = typeSplit[1].split(",")
				newEvent = Event(eType=2, pcData=pcData[0], pcRecip=pcData[1], consent=pcData[2].rstrip("\n"))
				eventList.append(newEvent)
				# print("Policy Change of data type {0}, recipient {1}, and {2} type consent".format(pcData[0], pcData[1], pcData[2].rstrip("\n")))
			
			#add data or recipients
			elif typeSplit[0] == "#":
				newData = typeSplit[1].split(">")
				newEvent = Event(eType=1, parent=newData[0], child=newData[1].rstrip("\n"))
				eventList.append(newEvent)
				# print("class {0} subsumes class {1} to be added".format(newData[0], newData[1].rstrip("\n")))
			
			else:
				#how often data collected, accessed
				# print(typeSplit)
				freqs = typeSplit[1].split(",")
				self.collectFreqs[typeSplit[0]] = float(freqs[0])
				self.accessFreqs[typeSplit[0]] = float(freqs[1].rstrip("\n"))
				# print("{0} class collect freq of {1} and access freq of {2}".format(typeSplit[0], freqs[0], freqs[1].rstrip("\n")))

		# print("\nCollect Freqs: ", self.collectFreqs)
		# print("accessFreqs: ", self.accessFreqs)

		# for e in eventList:
		# 	print("\ntype: ", e.getType())
		# 	print("arguments: ", e.getArgs())

		return eventList

	#creates a new timestep
	def nextTimeStep(self):
		prevTime = "T" + str(self.timeStep)
		self.timeStep += 1
		newTime = "T" + str(self.timeStep)

		self.simOnto.createNewClass(prevTime, newTime)
		return

	#adds a class to ontology: data type or recipient
	#dont need this method
	def addClass(self, parent, child):
		c = self.simOnto.createNewClass(parent, child)
		return c

	#creates a policy change
	def createPolicyChange(self, pcData, pcRecip, consent):
		print("Policy Change Occured")

		#store new pc
		newPolicy = (pcData, pcRecip, consent,)
		print("the new data type is subsumed by: ", self.simOnto.getClass(pcData).is_a)

	#collects specified datatypes from users
	def collectData(self, dtype):
		print("data was collected for ", dtype)
		#loop through users, call owlgen on them
		startRange = self.totalCollectionEvents + 1
		for i in range(self.totalUsersAdded - self.numUsersWithdrawn):
			#the this is set up it assumes that the users leaving are the oldest ones. (The consents created at T0 vs those leaving)
			#sets up which number user is collected
			num = i + self.numUsersWithdrawn + 1

			u = "U" + str(num)
			time = "T" + str(self.timeStep)

			# print("User: ", u, "time: ", time)

			#assumes data collected for all recipients
			self.simOnto.logDataCollection(dtype, u, time, "Recipient")

			self.totalCollectionEvents += 1

		return range(startRange, self.totalCollectionEvents + 1)

	#create access log events for users it can access data from
	def accessData(self, dtype, dcRange):
		print("data was accessed for data ", dtype)
		#find out which users it does NOT violate consents to access
		#create a data access log with OWLGEN for the indicated users

		#will need to get more specific with this part later
		time = "T" + str(self.timeStep)

		for i in dcRange:
			# dcNumber = self.totalCollectionEvents - i
			dc = 'dataCollection{0}'.format(i) #dcNumber


			#assumes data collected for all recipients
			self.simOnto.logDataAccess(dc, time, "Recipient")

		return

	'''adds a randomly generated (add perams later to be more specific) number of users to the simulation
	for now I have hardcoded the number of users to add, In the future I would like to add as a parameter


	MIGHT NEED TO ADJUST HANDLING FOR STATS CALC'''
	def addUsersInSim(self):
		#generates the number of users added
		minAdded = 5
		maxAdded = 15
		if self.users.sum() > 99:
			maxAdded = self.users.sum() // 6
		numAdded = random.randint(minAdded, maxAdded)
		# print("\nnum users added: ", numAdded)

		#calculates new user demographics
		newUserDemos = self.userProps * numAdded

		newUserDemos = newUserDemos.astype(int)
		#recalculates number of users added to account for rounding
		numAdded = newUserDemos.sum()
		print(numAdded, " users added")

		#adds the new users to the simulation
		for i in range(numAdded):
			userName = "U" + str(self.totalUsersAdded + i + 1)
			# print("userName: ", userName)
			self.simOnto.createNewClass("User", userName)

			#creates the initial consent as the user is added
			timeAdded = "T" + str(self.timeStep)
			cName = userName + "initialConsent"
			self.simOnto.userConsent("D1", userName, timeAdded, "R1", cName)

		self.totalUsersAdded += numAdded
		self.currentUsers = self.currentUsers + newUserDemos
		# print("done adding users\n")

		return





	def runSimulation(self):
		for e in self.eventList:
			#e.get args returns [parent, child, pcData, pcRecip, consent]
			eType = e.getType()

			if eType == 0:
				#next time interval
				#better to just increment, throw out method?
				self.nextTimeStep()
				self.addUsersInSim()

				#as timestep increases, randomly check if data is collected or accessed:
				#if accessed, call the data access collect methods, which collect and access data for recipients
				#in dataAccess? check for violations
				prob = random.random()
				# print("probability: ", prob)
				# print("dc dict: ", self.collectFreqs)

				for data, freq in self.collectFreqs.items():
					# print("data tested: ", data)
					# print("freq of dC: ", freq)
					if freq > prob:
						# print("data collected")
						# print("data collecting now: ", data)
						self.dcNumRange[data] = self.collectData(data)
				print("dict for numbers: ", self.dcNumRange)
				
				for data, freq in self.accessFreqs.items():
					# print("freq of dA: ", freq)
					if data in self.dcNumRange:
						if freq > prob:
							# print("data accessed")
							self.accessData(data, self.dcNumRange[data])


			elif eType == 1:
				#add class (data or recipient)
				args = e.getArgs()
				self.simOnto.createNewClass(args[0], args[1])

				#or could call:
				# self.addClass(args[0], args[1])
			elif eType == 2:
				args = e.getArgs()
				self.createPolicyChange(args[2], args[3], args[4])


		self.simOnto.save(self.name)



#class that takes the data read from the script and calls the correct event method.
#should event have the meat of what happens with each event, or should simulation? it feels like it should go in sim, but would be eaiser to go in event
#could call return type, indecating what type of Sim method to call, and then return the needed data
class Event:
	def __init__(self, eType=0, parent=None, child=None, pcData=None, pcRecip=None, consent=None):
		#0 for next time interval, 1 for adding data or recipients, 2 a policy change
		self.eType = eType

		#used when adding new data or recipents (type 1)
		self.parent = parent
		self.child = child

		#used for policy change (type 2)
		self.pcData = pcData
		self.pcRecip = pcRecip
		self.consent = consent


	#returns event type
	def getType(self):
		return self.eType

	#returns the perameters of the event in list form
	def getArgs(self):
		return [self.parent, self.child, self.pcData, self.pcRecip, self.consent]


def main():
	startTime = time.time()
	mySim = Simulation("testPop.txt", "testScript.txt", "http://SimTest1.org/myonto")
	mySim.runSimulation()
	stopTime = time.time()

	print("\n\n\nruntime: ", stopTime - startTime)

if __name__ == "__main__":
	main()


