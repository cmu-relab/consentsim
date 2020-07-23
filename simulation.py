'''
7/9/20
Simulation.py
'''
import OWLgenerator as ow
import numpy as np
import random
import time
import scriptParser



class Simulation:
	
	def __init__(self, userTable, withdrawTable, owlIRI, multiplyer=0):
		self.iri = owlIRI
		self.numCopies = 0
		self.numDestroyed = 0
		self.daNum = 0
		self.oldDCs = []
		self.allDAs = []
		#contains the number of users in each demographic
		self.userTable = userTable

		self.mult = int(multiplyer)

		#contains which timestep program is in
		self.timeStep = 0

		#contains the owl ontology knowladge base.
		self.simOnto = ow.OWLgenerator(owlIRI)

		#parse contingency table demoCols/Rows are col/row lables
		#users are the actual numbers of users data, userRrops are the calculated proportions users in each demographic category
		self.demoCols, self.demoRows, self.users, self.userProps = self.parseTable(userTable)
		# print("mult: ", multiplyer, " users in table: ", self.users.sum())
		# self.users = self.users + int(multiplyer)
		# self.users = self.users.astype(int)
		print("number of Users: ", self.users.sum())
		self.withdrawProb = self.parseWithdraw(withdrawTable)

		# Table of number of current users in each demographic, gets updated as user numbers change
		self.currentUsers = self.users

		#tracks the total number of users added through simulation
		#mainly for naming and access purposes
		self.totalUsersAdded = self.users.sum()
		print("tna ", self.totalUsersAdded)

		#tracks the number of dataCollection instances made
		self.totalCollectionEvents = 0

		#a list of active users
		self.activeUsers = []

		#the minimum and maximum number of users that may be added within each timestep
		self.minAdded = 5
		self.maxAdded = 15

		#adds initial users to the ontology
		#should make separate method for this
		for i in range(1, self.totalUsersAdded+1):
			newU = "U" + str(i)
			print(newU, " added")
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
		#allows access to access the proper dataCollection log for specific user and data type
		self.dcNumRange = {}

		#to track which users to withdraw consent, and how many to collect/access data from
		self.numUsersWithdrawn = 0

		#tracks the current and past policies
		self.initialPolicy = ("D1", "Recipient", "cr",)
		self.currentPolicy = ("D1", "Recipient", "cr",)

		#a list of all past and current policies
		#I do not use this to any useful extent
		#but it may be useful as number of policies becomes more complex or want more stats
		self.policies = [self.initialPolicy]

		#parse script
		# self.eventList = self.parseScript(simScript)

		# print(self.activeUsers)

		# with change dont need
		# self.name = simScript[:-3] + "owl"


		# f = open("newOntos100TimeSteps.csv", "w")
		# f.write("Timestep, Time (s)")
		# f.close()

	#update min added 
	def setMinAdded(self, minimum):
		self.minAdded = minimum

	#update max added
	def setMaxAdded(self, maximum):
		self.maxAdded = maximum

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

		users = users + self.mult

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

	#creates a new timestep
	def nextTimeStep(self):
		prevTime = "T" + str(self.timeStep)
		self.timeStep += 1
		newTime = "T" + str(self.timeStep)

		print("time step: ", self.timeStep)

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
		numInit = len(self.activeUsers)

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


		count = 0
		for i in range(self.numUsersWithdrawn, self.numUsersWithdrawn + numLeave):
			if len(self.activeUsers) == 0:
				numLeave = count
				break
			u = "U" + str(i+1)

			self.activeUsers.remove(u)

			count += 1

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
		# print("instances of this user: ", self.simOnto.searchClass("U1"))
		# print("the new data type is subsumed by: ", self.simOnto.getClass(pcData).is_a)

		return (numLeave, len(self.policies)-1, len(self.activeUsers), numInit)

	#parses the str of the consent class to return the data type in consent
	def parseConsent(self, consentStr, retroactive):
		s = consentStr.split(".")
		data = None
		if retroactive:
			data = s[-1][:-1]
			return data
		else:
			return None

	#checks if there is user consent for data access
	def checkConsent(self, u, d, t):
		#need to remember to call the reasoner right before - can't call in method because it takes forever

		#will need to update to handle withdrawals
		userQuery = self.simOnto.searchConsents(self.simOnto.getClass(u))
		# print(userQuery)
		allConsents = []
		if len(userQuery) > 1:
			allConsents = userQuery[1:]
		else:
			return False

		# check that is for the proper data type
		#need to check access relationships, must be way
		for c in allConsents:
			parts = self.simOnto.getClassInfo(c)
			# print("Parts of c: ", parts)
			complexParts = str(parts[0])

			#check consent type to prep for parseConsent
			cName = str(parts[1])
			cType = False
			if cName[7] == "r":
				cType = True
			# print("retroactive: ", cType)


			#gets data type of the consent
			dtype = self.parseConsent(complexParts, cType)
			# print("does data type match? ", dtype, d)
			# print("dType of consent: ", dtype)

			if d == dtype:
				# print("matched, should collect data for ", d)
				return True


		#check that time is current
		return False

	#collects specified datatypes from users
	def collectData(self, dtype):
		print("data was collected for ", dtype)

		# # self.simOnto.reason()
		# startTime = time.time()
		# self.simOnto.reason()
		# stopTime = time.time()

		# finalTime = stopTime - startTime

		# f = open("10Users50timestepsTime.csv", "a")
		# f.write(self.timeStep, finaltime)
		# f.close()

		#append how long reasoner takes
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
			# print("Time for user ", u, "at time step ", t)
			t = "T" + str(self.timeStep)
			print("Time for user ", u, "at time step ", t)
			consents = self.checkConsent(u, dtype, t)
			# print("result of consents: ", consents)
			# print("consent allowed: ", consents)
			if consents:
				# print("Consent veerified, data collected")
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
			self.daNum += 1
			self.allDAs.append(self.daNum)
			# dcNumber = self.totalCollectionEvents - i
			dcStr = 'dataCollection{0}'.format(i) #dcNumber

			dc = self.simOnto.getDataCollection(dcStr)

			if dc == None:
				continue

			#creates access log
			self.simOnto.logDataAccess(dc, time, "Recipient")

		return

	'''checks if data is collected and accessed from each user by random probability
	if accessed or collected it creates the appropriate logs in the knowlage base
	and updates dictionarys accordingly'''
	def updateDataLogs(self):
		#in dataAccess? check for violations
		# startTime = time.time()
		# self.simOnto.reason()
		# stopTime = time.time()

		# self.simOnto.reason()
		startTime = time.time()
		self.simOnto.reason()
		stopTime = time.time()

		finalTime = stopTime - startTime

		# if self.timeStep == 1:
		# 	f = open("newOntos.csv", "a")
		# 	f.write("\n{0},{1}".format(self.users.sum(), finalTime))
		# 	f.close()
		# elif self.timeStep == 5 or self.timeStep == 10:
		# 	f = open("newOntos.csv", "a")
		# 	f.write(",{0}".format(finalTime))
		# 	f.close()

		# f = open("newOntos100TimeSteps.csv", "a")
		# f.write("\n{0},{1}".format(self.timeStep, finalTime))
		# f.close()


		# timeToReason = stopTime - startTime

		# files = open to append
		#append time to reason, do not newline

		#to compare to frequency
		prob = random.random()

		for data, freq in self.collectFreqs.items():
			if freq > prob:
				#store old dc ranges
				if data in self.dcNumRange:
					self.oldDCs.extend(self.dcNumRange[data])

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
		# self.minAdded = 5
		# self.maxAdded = 15
		# maxAdd = self.maxAdded
		# if self.users.sum() > 99:
		# 	maxAdded = self.users.sum() // 6
		numAdded = random.randint(self.minAdded, self.maxAdded)
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
		print("prev total users addded: ", self.totalUsersAdded)

		self.totalUsersAdded += numAdded
		print("after total users added: ", self.totalUsersAdded)
		self.currentUsers = self.currentUsers + newUserDemos
		# print("done adding users\n")

		return

	#transfers relevent classes, timesteps to a new ontology
	#deletes non active users, data accesses, and old data collections(for now)
	#do all the classes for time steps affect how long the reasoner takes? maybe.
	def copyOnto(self):
		print("doing this")
		#saves old owl file
		# self.numCopies += 1
		# name = "UpdateFile" + str(self.numCopies) + ".owl"
		# self.simOnto.save(name)

		# #get new ontology
		# newOnto = ow.OWLgenerator(self.iri, False)

		#delete users that left

		while self.numDestroyed != self.numUsersWithdrawn:
			u = "U" + str(self.numDestroyed+1)
			c = u + "initialConsent"
			# print(c)
			self.simOnto.deleteEntity(c)
			self.simOnto.deleteEntity(u)
			self.numDestroyed += 1

		# n = 0
		# for i in range(self.numDestroyed, self.numUsersWithdrawn):
		# 	u = "U" + str(i+1)
		# 	c = u + "initialConsent"
		# 	print(c)
		# 	self.simOnto.deleteEntity(c)
		# 	n =+ 1

		# self.numDestroyed += n

		#deletes all data collections
		for dc in self.oldDCs:
			dcName = 'dataCollection{0}'.format(dc)

			# print(dcName, " DELETED")

			self.simOnto.deleteEntity(dcName)
		self.oldDCs = []

		for da in self.allDAs:
			daName = "dataAccess{0}".format(da)

			self.simOnto.deleteEntity(daName)
		self.allDAs = []

		# self.simOnto = newOnto

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


