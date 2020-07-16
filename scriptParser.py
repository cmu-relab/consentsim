#!env/bin/python3
import simulation as sim
import OWLgenerator as ow
import numpy as np
import random
import time


'''class that loops through the script file
At each line of the file it calls appropriate methods to carry out events'''
class ScriptParser:

	#takes in script
	def __init__(self, script, simulation, save=True):

		self.script = script
		self.sim = simulation
		self.save = save

		self.resultsName = script[:-4] + "Results.csv"

		#set up results csv
		f = open(self.resultsName, "w")
		f.write("Policy Change Number,Number of users Quit,Number Users Ramaining")

	#parses and runs script
	def parseScript(self):

		#open script
		file = open(self.script, "r")

		#loop through file
		for line in file:

			#time step
			if line[0] == "^":
				#increments time step and adds the next time step to the ontology
				self.sim.nextTimeStep()
				
				#adds random number of users to sim
				self.sim.addUsersInSim()
				
				#collects and accesses data based on probability
				self.sim.updateDataLogs()

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
				numLeft, numPolicy, numRemain = self.sim.createPolicyChange(dtype, recip, consent)

				f = open(self.resultsName, "a")
				f.write("\n{0},{1},{2}".format(numPolicy, numLeft, numRemain))
				f.close()

			#is the update for frequency of data collection and access
			else:
				#parse frequency
				dtype, cFreq, aFreq = self.parseFreq(line)

				#updated dictionaries with frequencies
				self.sim.updateCollectionFreq(dtype, aFreq)
				self.sim.updateAccessFreq(dtype, cFreq)

		#close file
		file.close()

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
		dtype = sp[0]

		#splits to get collection, access frequencies
		f = sp[1].split(",")

		return dtype, float(f[0]), float(f[1].rstrip("\n"))



def main():
	startTime = time.time()


	mySim = sim.Simulation("testPop.txt", "testWithdraw.txt", "http://SimTest1.org/myonto")
	myParser = ScriptParser("testScript.txt", mySim)
	myParser.parseScript()
	# mySim.runSimulation()


	stopTime = time.time()
	print("Users: ", mySim.activeUsers)

	print("\n\n\nruntime: ", stopTime - startTime)

if __name__ == "__main__":
	main()
