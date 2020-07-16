'''
7/9/20
Simulation.py
'''
import OWLgenerator as ow
import numpy as np
import random
import time



class Simulation:
	
	def __init__(self, userTable, withdrawTable, owlIRI):
		#contains which timestep program is in
		self.userTable = userTable
		self.timeStep = 0

		self.simOnto = ow.OWLgenerator(owlIRI)

		#parse contingency table demoCols/Rows are col/row lables
		#users are the actual numbers of users data, userRrops are the calculated proportions users in each demographic category
		self.demoCols, self.demoRows, self.users, self.userProps = self.parseTable(userTable)
		self.withdrawProb = self.parseWithdraw(withdrawTable)

		self.currentUsers = self.users

		self.totalUsersAdded = self.users.sum()

		self.totalCollectionEvents = 0

		self.activeUsers = []

		#adds users to the ontology
		#should make separate method for this
		for i in range(1, self.totalUsersAdded+1):
			newU = "U" + str(i)
			self.activeUsers.append(newU)
			cName = newU + "initialConsent"
			self.simOnto.createNewClass("User", newU)

			#had before ("D1", newU, "T0", "Recipient", cName) - easier to take out user,
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
		self.currentPolicy = ("D1", "Recipient", "cr",)
		self.policies = [self.initialPolicy]

		#parse script
		# self.eventList = self.parseScript(simScript)

		# with change dont need
		# self.name = simScript[:-3] + "owl"

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

	#parses the table that indecates chances of withdrawing
	def parseWithdraw(self, withdrawTable):
		file = open(withdrawTable, "r")
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

		users = table[1:, 1:].astype(float)

		return users


	# #parses the script for the simulation into a useful data structure
	# def parseScript(self, simScriptTxt):
	# 	file = open(simScriptTxt, "r")
	# 	eventList = []

	# 	# print("\n\n\nremember to uncomment events\n\n\n")
	# 	for line in file:
	# 		typeSplit = line.split(":")

	# 		newEvent = None


	# 		#new time interval
	# 		if typeSplit[0].rstrip("\n") == "^":
	# 			newEvent = Event()
	# 			eventList.append(newEvent)
	# 			# print("New Time step!")

	# 		#policy change
	# 		elif typeSplit[0] == "+":
	# 			pcData = typeSplit[1].split(",")
	# 			newEvent = Event(eType=2, pcData=pcData[0], pcRecip=pcData[1], consent=pcData[2].rstrip("\n"))
	# 			eventList.append(newEvent)
	# 			# print("Policy Change of data type {0}, recipient {1}, and {2} type consent".format(pcData[0], pcData[1], pcData[2].rstrip("\n")))
			
	# 		#add data or recipients
	# 		elif typeSplit[0] == "#":
	# 			newData = typeSplit[1].split(">")
	# 			newEvent = Event(eType=1, parent=newData[0], child=newData[1].rstrip("\n"))
	# 			eventList.append(newEvent)
	# 			# print("class {0} subsumes class {1} to be added".format(newData[0], newData[1].rstrip("\n")))
			
	# 		else:
	# 			#how often data collected, accessed
	# 			# print(typeSplit)
	# 			freqs = typeSplit[1].split(",")
	# 			self.collectFreqs[typeSplit[0]] = float(freqs[0])
	# 			self.accessFreqs[typeSplit[0]] = float(freqs[1].rstrip("\n"))
	# 			# print("{0} class collect freq of {1} and access freq of {2}".format(typeSplit[0], freqs[0], freqs[1].rstrip("\n")))

	# 	# print("\nCollect Freqs: ", self.collectFreqs)
	# 	# print("accessFreqs: ", self.accessFreqs)

	# 	# for e in eventList:
	# 	# 	print("\ntype: ", e.getType())
	# 	# 	print("arguments: ", e.getArgs())

	# 	return eventList

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
		# print("Policy Change Occured")

		t = "T" + str(self.timeStep)

		#store new pc
		newPolicy = (pcData, pcRecip, consent,)

		retro = True

		if consent == "cn":
			retro = False
		# self.policies.append(newPolicy)

		#reason to determine what users have which consents
		# self.simOnto.reason()

		#determine how many users will accept and how many leave - table?
		leaveTable = self.withdrawProb * self.users
		numLeave = int(leaveTable.sum())
		print("Policy Change Occured, ", numLeave, " users left")


		for i in range(self.numUsersWithdrawn, self.numUsersWithdrawn + numLeave):
			u = "U" + str(i+1)

			self.activeUsers.remove(u)

		self.numUsersWithdrawn += numLeave

		#Users who leave - Do not create consent. Later maybe create withdrawal - by starting at beginning after num users withdrawn

		#Users who consent - can create consent starting at last withdrawn in previous loop up to total users
		#Change to a for loop?
		i = self.numUsersWithdrawn
		while i < self.totalUsersAdded:
			i += 1

			u = "U" + str(int(i))
			cName = u + "policyChange" + str(len(self.policies))
			self.simOnto.userConsent(pcData, u, t, pcRecip, cName, retro)



		#add the new policy to list
		self.policies.append(newPolicy)
		#save new policy as current policy
		self.currentPolicy = newPolicy

		#save num who leave, num who consent, report these stats

		#have to reason before calling search
		print("instances of this user: ", self.simOnto.searchClass("U1"))
		print("the new data type is subsumed by: ", self.simOnto.getClass(pcData).is_a)

		return (numLeave, len(self.policies)-1, len(self.activeUsers))

	#checks if there is user consent for data access
	def checkConsent(self):
		#need to remember to call the reasoner right before - can't call in method because it takes forever
		return

	#collects specified datatypes from users
	def collectData(self, dtype):
		print("data was collected for ", dtype)
		#loop through users, call owlgen on them
		startRange = self.totalCollectionEvents + 1
		# for i in range(self.totalUsersAdded - self.numUsersWithdrawn):
		# 	#the this is set up it assumes that the users leaving are the oldest ones. (The consents created at T0 vs those leaving)
		# 	#sets up which number user is collected
		# 	num = i + self.numUsersWithdrawn + 1

		# 	u = "U" + str(num)
		# 	time = "T" + str(self.timeStep)

		# 	# print("User: ", u, "time: ", time)

		# 	#assumes data collected for all recipients
		# 	self.simOnto.logDataCollection(dtype, u, time, "Recipient")

		# 	self.totalCollectionEvents += 1

		for u in self.activeUsers:
			t = "T" + str(self.timeStep)
			self.simOnto.logDataCollection(dtype, u, t, self.currentPolicy[1])
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
			dcStr = 'dataCollection{0}'.format(i) #dcNumber

			dc = self.simOnto.getDataCollection(dcStr)


			#assumes data collected for all recipients
			self.simOnto.logDataAccess(dc, time, "Recipient")

		return

	'''checks if data is collected and accessed from each user by random probability
	if accessed or collected it creates the appropriate logs in the knowlage base
	and updates dictionarys accordingly'''
	def updateDataLogs(self):
		#in dataAccess? check for violations

		#to compare to frequency
		prob = random.random()

		for data, freq in self.collectFreqs.items():
			if freq > prob:
				#collect data
				self.dcNumRange[data] = self.collectData(data)		
				
		for data, freq in self.accessFreqs.items():
			#access data
			if data in self.dcNumRange:
				#checks that appropriate data has been collected
				if freq > prob:
					self.accessData(data, self.dcNumRange[data])


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

		retro = True
		if self.currentPolicy[2] == "cn":
			retro = False

		#adds the new users to the simulation
		for i in range(numAdded):
			userName = "U" + str(self.totalUsersAdded + i + 1)
			self.activeUsers.append(userName)
			# print("userName: ", userName)
			self.simOnto.createNewClass("User", userName)

			#creates the initial consent as the user is added
			timeAdded = "T" + str(self.timeStep)
			cName = userName + "initialConsent"
			self.simOnto.userConsent(self.currentPolicy[0], userName, timeAdded, self.currentPolicy[1], cName, retro)

		self.totalUsersAdded += numAdded
		self.currentUsers = self.currentUsers + newUserDemos
		# print("done adding users\n")

		return

	#creates new class in OWL ontology
	def addOntoClass(self, parent, newClass):
		self.simOnto.createNewClass(parent, newClass)
		return

	#updates the dictionary for collection frequency
	def updateCollectionFreq(self, data, freq):
		self.collectFreqs[data] = freq
		return

	#updates the dictionary for access frequency
	def updateAccessFreq(self, data, freq):
		self.accessFreqs[data] = freq
		return

	#saves ontology
	def saveOnto(self, name):
		self.simOnto.save(name)
		return


# '''class that loops through the script file
# At each line of the file it calls appropriate methods to carry out events'''
# class ScriptParser:

# 	#takes in script
# 	def __init__(self, script, simulation, save=True):

# 		self.script = script
# 		self.sim = simulation
# 		self.save = save

# 		self.resultsName = script[:-4] + "Results.csv"

# 		#set up results csv
# 		f = open(self.resultsName, "w")
# 		f.write("Policy Change Number,Number of users Quit,Number Users Ramaining")

# 	#parses and runs script
# 	def parseScript(self):

# 		#open script
# 		file = open(self.script, "r")

# 		#loop through file
# 		for line in file:

# 			#time step
# 			if line[0] == "^":
# 				#increments time step and adds the next time step to the ontology
# 				self.sim.nextTimeStep()
				
# 				#adds random number of users to sim
# 				self.sim.addUsersInSim()
				
# 				#collects and accesses data based on probability
# 				self.sim.updateDataLogs()

# 			#add class
# 			elif line[0] == "#":
# 				#parses arguments for adding class
# 				p, c = self.parseClassAddition(line)

# 				#adds the classes to the ontology
# 				self.sim.addOntoClass(p, c)

# 				# print("Class added: ", self.sim.get)

# 			#policy change
# 			elif line[0] == "+":
# 				#parses the policy change
# 				dtype, recip, consent = self.parsePolicyChange(line)

# 				#call method in sim to inact the policy change
# 				numLeft, numPolicy, numRemain = self.sim.createPolicyChange(dtype, recip, consent)

# 				f = open(self.resultsName, "a")
# 				f.write("\n{0},{1},{2}".format(numPolicy, numLeft, numRemain))
# 				f.close()

# 			#is the update for frequency of data collection and access
# 			else:
# 				#parse frequency
# 				dtype, cFreq, aFreq = self.parseFreq(line)

# 				#updated dictionaries with frequencies
# 				self.sim.updateCollectionFreq(dtype, aFreq)
# 				self.sim.updateAccessFreq(dtype, cFreq)

# 		#close file
# 		file.close()

# 		#saves file if True
# 		if self.save == True:
# 			#creates name for file based on script name
# 			name = self.script[:-3] + "owl"
# 			#saves file
# 			self.sim.saveOnto(name)

# 	'''parses line to add class to ontology
# 	returns parent class, new class to be added'''
# 	def parseClassAddition(self, line):
# 		#remove flag for line type
# 		l = line[1:]

# 		#splits into the two classes
# 		classes = l.split(">")

# 		#returns the two classes
# 		return classes[0], classes[1].rstrip("\n")

# 	''' parses line to create a policy change
# 	returns data type, recipient, consent type'''
# 	def parsePolicyChange(self, line):
# 		#remove tag for line type
# 		l = line[1:]

# 		#splits via commas into the 3 data types
# 		components = l.split(",")

# 		return components[0], components[1], components[2].rstrip("\n")

# 	'''parses frequencies of access and collecion
# 	returns datatype, collection frequency, access frequency'''
# 	def parseFreq(self, line):
# 		#splits to separate dtype from freqs
# 		sp = line.split(":")
# 		dtype = sp[0]

# 		#splits to get collection, access frequencies
# 		f = sp[1].split(",")

# 		return dtype, float(f[0]), float(f[1].rstrip("\n"))



# def main():
# 	startTime = time.time()


# 	mySim = Simulation("testPop.txt", "testWithdraw.txt", "http://SimTest1.org/myonto")
# 	myParser = ScriptParser("testScript.txt", mySim)
# 	myParser.parseScript()
# 	# mySim.runSimulation()


# 	stopTime = time.time()
# 	print("Users: ", mySim.activeUsers)

# 	print("\n\n\nruntime: ", stopTime - startTime)

# if __name__ == "__main__":
# 	main()


