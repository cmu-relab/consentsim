
import simulation as sim
import OWLgenerator as ow
import numpy as np
import random
import time
import csv
import sys


'''class that loops through the script file
At each line of the file it calls appropriate methods to carry out events'''
class ScriptParser:

	#takes in script
	def __init__(self, script, simulation, save=True):

		self.script = script
		self.sim = simulation
		self.save = save

		self.resultsName = script[:-4] + "PolicyChangeResults.csv"
		self.timeName = script[:-4] + "TimeStepResults.csv"
		self.allLogData = script[:-4] + "LogEvents.csv"

		self.allDataTypes = ["Timestep"]

		#set up pc results csv
		f = open(self.resultsName, "w")
		f.write("Policy Change Number,Initial Number of Users,Number of users Quit,Number Users Ramaining")
		f.close()

		f = open(self.timeName, "w")
		f.write("Timestep, Users joined, Total Users, number data collections,number data accesses,time taken")
		f.close()

	#parses and runs script
	def parseScript(self):

		#open script
		file = open(self.script, "r")

		#loop through file
		for line in file:

			#time step
			if line[0] == "^":
				startTime = time.time()
				#increments time step and adds the next time step to the ontology
				t = self.sim.nextTimeStep()
				
				#adds random number of users to sim
				numJoin, numTotal = self.sim.addUsersInSim()
				
				#collects and accesses data based on probability
				numDc, numDa, allLogs, timeTaken = self.sim.updateDataLogs()

				#copies over new onto so timesteps dont take as long
				self.sim.copyOnto()

				endTime = time.time()

				runTime = endTime - startTime

				f = open(self.timeName, "a")
				f.write("\n{0},{1},{2},{3},{4},{5}".format(t, numJoin, numTotal, numDc, numDa, runTime))
				f.close()


			#add class
			elif line[0] == "#":
				#parses arguments for adding class
				p, c = self.parseClassAddition(line)

				#adds the classes to the ontology
				self.sim.addOntoClass(p, c)

				# print("Class added: ", self.sim.get)

			#policy change
			elif line[0] == "+":
				#parses the policy change
				dtype, recip, consent = self.parsePolicyChange(line)

				#call method in sim to inact the policy change
				numLeft, numPolicy, numRemain, numInit = self.sim.createPolicyChange(dtype, recip, consent)

				f = open(self.resultsName, "a")
				f.write("\n{0},{1},{2},{3}".format(numPolicy, numInit, numLeft, numRemain))
				f.close()

			#update minAdded and MaxAdded for number of users added per timestep
			elif line[0] == "%":
				# %+ is max added
				if line[1] == "+":
					newMax = int(line[2:])
					self.sim.setMaxAdded(newMax)
				else:
					# %- is min added
					newMin = int(line[2:])
					self.sim.setMinAdded(newMin)

			#is the update for frequency of data collection and access
			else:
				#parse frequency
				print("line for freq: ", line)
				dtype, cFreq, aFreq = self.parseFreq(line)

				#updated dictionaries with frequencies
				dtypeLog = self.sim.updateCollectionFreq(dtype, cFreq)
				self.sim.updateAccessFreq(dtype, aFreq)

				if dtype != None:
					self.allDataTypes.append(dtypeLog)

		#close file
		file.close()

		#writes data stats to csv
		self.sim.statsToCSV(self.allLogData)

		#saves file if True
		if self.save == True:
			#creates name for file based on script name
			name = self.script[:-3] + "owl"
			#saves file
			self.sim.saveOnto(name)

	'''parses line to add class to ontology
	returns parent class, new class to be added'''
	def parseClassAddition(self, line):
		#remove flag for line type
		l = line[1:]

		#splits into the two classes
		classes = l.split(">")

		#returns the two classes
		return classes[0], classes[1].rstrip("\n")

	''' parses line to create a policy change
	returns data type, recipient, consent type'''
	def parsePolicyChange(self, line):
		#remove tag for line type
		l = line[1:]

		#splits via commas into the 3 data types
		components = l.split(",")

		return components[0], components[1], components[2].rstrip("\n")

	'''parses frequencies of access and collecion
	returns datatype, collection frequency, access frequency'''
	def parseFreq(self, line):
		#splits to separate dtype from freqs
		sp = line.split(":")
		# print("Spit at : : ", sp)
		dtype = sp[0]

		#splits to get collection, access frequencies
		f = sp[1].split(",")

		return dtype, float(f[0]), float(f[1].rstrip("\n"))



def main():
	startTime = time.time()

	mySim = sim.Simulation("testPop.txt", "testWithdraw.txt", "http://SimTest1.org/myonto")
	myParser = ScriptParser(sys.argv[1], mySim)
	myParser.parseScript()


	stopTime = time.time()
	print("Users: ", mySim.activeUsers)

	print("\n\n\nruntime: ", stopTime - startTime)

if __name__ == "__main__":
	main()
