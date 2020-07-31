from owlready2 import *
import types
import argparse

class OWLgenerator:

	def __init__(self, iri, create_new=True, copy=True):
		self.dc_counter = 1
		self.ac_acount = 1
		self.onto = None

		#for argparse
		# self.parser = argparse.ArgumentParser()

		# self.parser.add_argument("--c", "--consent", nargs=6)

		#loads or creates ontology
		if create_new:
			self.onto = self.createBaseOntology(iri)
			self.baseForTest()
		else:
			self.onto = get_ontology(iri).load()

	'''returns ontology used in base of simulation
	creates Data, Recipient, User, (n)rConsent/Withdrawal, Time (T0 - T3) classes, and object property access '''
	def createBaseOntology(self, iri):
		o = get_ontology(iri)
		with o:
			class Data(Thing):
				pass
			class Recipient(Thing):
				pass
			class User(Thing):
				pass
			class rConsent(Thing):
				pass
			class nrConsent(Thing):
				pass
			class rWithdrawal(Thing):
				pass
			class nrWithdrawal(Thing):
				pass
			class Time(Thing):
				pass
			class T0(Time):
				pass
			# class T1(T0):
			# 	pass
			# class T2(T1):
			# 	pass
			# class T3(T2):
			# 	pass
			class access(ObjectProperty, AsymmetricProperty):
				pass
		return o

	'''adds D1, D2, R1, R2, R3, U1 to the base ontology for our testing puropses'''
	def baseForTest(self):
		#should add a check to make sure it is adding onto an ontology with the necessary classes: check for Data, Recipient, User
		#should also check not already D1, D2, R1, R2, R3, or U1
	 	with self.onto:
	 		class D1(self.onto.Data):
	 			pass
	 		class D2(self.onto.Data):
	 			pass
	 		class R1(self.onto.Recipient):
	 			pass
	 		class R2(self.onto.R1):
	 			pass
	 		class R3(self.onto.Recipient):
	 			pass
	 		class U1(self.onto.User):
	 			pass
	 	return

	'''returns class in the ontology
	mainly so methods creating classses can access classes passed in as stirngs in perameters
	c is either a string or a class'''
	def getClass(self, c):
		if isinstance(c, str):
			# print(c)
			# print("O: ", self.onto[c])
			return self.onto[c]
		else:
			return c

	'''returns a dataCollection object'''
	def getDataCollection(self, d):
		if isinstance(d, str):
			return self.onto[d]
		else:
			return d


	'''creates a consent class of the given name using classes D, U, T, and R passed in all as strings
	if retroactive is True, consent will be retroactive, otherwise will be non retroactive'''
	def userConsent(self, Dx, Uy, Tz, Rw, className, retroactive=True):
		createConsent = None
		if retroactive:
			#is subsumed by (T and U) or access(D)
			createdConsent = types.new_class(className, (self.onto.rConsent,), {}	)
			createdConsent.is_a = [(self.getClass(Tz) & self.getClass(Uy)) | self.onto.access.some(self.getClass(Dx))]
			createdConsent.is_a.append(self.onto.rConsent)

		else:
			#non-retroactive Consent: subsumed by (T and U) or access(D and T)
			createdConsent = types.new_class(className, (self.onto.nrConsent,), {}	)
			createdConsent.is_a = [(self.getClass(Tz) & self.getClass(Uy)) | self.onto.access.some(self.getClass(Dx) & self.getClass(Tz))]
			createdConsent.is_a.append(self.onto.nrConsent)

		#is equivalent to (T and U)
		createdConsent.equivalent_to = [self.getClass(Tz) & self.getClass(Uy)]

		return createConsent

	'''creates a withdrawal class of name className using classes D, U, T, and R passed in all as strings
	creates retroactive/non-retroactive withdrawal if retroactive argument is True/False'''
	def userWithdrawal(self, Dx, Uy, Tz, Rw, className, retroactive=True):
		createdWithdrawal = None
		if retroactive:
			#is subsumed by (T and U) and not access(D)
			createdWithdrawal = types.new_class(className, (self.onto.rWithdrawal,), {}	)
			createdWithdrawal.is_a = [(self.getClass(Tz) & self.getClass(Uy)) & Not(self.onto.access.some(self.getClass(Dx)))]
			createdWithdrawal.is_a.append(self.onto.rWithdrawal)
		else:
			#is subsumed by (T and U) and not access(D and T)
			createdWithdrawal = types.new_class(className, (self.onto.nrWithdrawal,), {}	)
			createdWithdrawal.is_a = [(self.getClass(Tz) & self.getClass(Uy)) & Not(self.onto.access.some(self.getClass(Dx) & self.getClass(Tz)))]
			createdWithdrawal.is_a.append(self.onto.nrWithdrawal)

		#is equivalent to (T and U)
		createdWithdrawal.equivalent_to = [self.getClass(Tz) & self.getClass(Uy)]

		return createdWithdrawal


	'''creates a dataCollection individual of passed in types D, U, R, and T'''
	def logDataCollection(self, Dx, Uy, Tz, Rw):
		#creates name for instance
		# print("starting log for ", Uy)
		name = 'dataCollection%i' % self.dc_counter

		#gets class D of instance
		classD = self.getClass(Dx)

		#creates instance using only class D, as I do not beileve it can be created with >1, although unsure
		individual = classD(name)

		#changes the type of the instance from D to (D and U and T and R)
		individual.is_a = [self.getClass(Dx) & self.getClass(Uy) & self.getClass(Tz) & self.getClass(Rw)]

		#increment for naming
		self.dc_counter += 1

		return individual




	'''creates a data access individual at R and T and access value dataCollection
	dc must be passed in as a dataCollection object, not a string'''
	def logDataAccess(self, dc, Tz, Rw):
		#creates name for the instance
		name = 'dataAccess%i' % self.ac_acount
		#gets class for T of instance
		classT = self.getClass(Tz)
		#creates using class T, as do not believe it is possible to create a complex individual this way
		individual = classT(name)

		#change the individuals type from T to (R and T and access dataCollection)
		individual.is_a =  [self.getClass(Rw) & self.getClass(Tz) & self.onto.access.value(dc)]

		#increment for naming purposes
		self.ac_acount += 1

		return individual


	'''creates a new class'''
	def createNewClass(self, parent, newClass):
		#gets parent class
		p = self.getClass(parent)

		#creates class that inherits from parent class p
		c = types.new_class(newClass, (p,), {}	)

		return c

	def getClassInfo(self, c):
		# return self.onto.search(subclass_of=self.getClass(c))
		return self.getClass(c).is_a

	def onlyConsents(self, t):
		return self.onto.search(type=t)

	def searchConsents(self, query):
		# print("search called")
		return self.onto.search(subclass_of=query)

	#deletes specified class
	def deleteEntity(self, e):
		delete = self.getClass(e)

		if delete != None:
			destroy_entity(delete)

		return





	'''uses a reasoner to make inferences and check consistancy'''
	def reason(self):

		with self.onto:
			#sync the reasoner
			sync_reasoner()

		#check for inconsistant classes, print if there are some
		ic = list(default_world.inconsistent_classes())
		if ic == []:
			print("\n")
		else:
			print("Inconsistant Classes:\n", ic)




	'''saves KB to file
	when called, filename must have .owl at the end or it will not be saved as an owl file'''
	def save(self, filename):
		self.onto.save(filename)

def main():
	my_onto = OWLgenerator("http://test.org/myonto", create_new=True)
	my_onto.baseForTest()

	rC1 = my_onto.userConsent("D1", "U1", "T1", "R1", "rC1")
	rC2 = my_onto.userConsent("D2", "U1", "T2", "R2", "rC2")
	nrC1 = my_onto.userConsent("D1", "U1", "T1", "R1", "nrC1", retroactive=False)

	rW1 = my_onto.userWithdrawal("D1", "U1", "T1", "R1", "rW1")
	nrW1 = my_onto.userWithdrawal("D1", "U1", "T1", "R1", "nrW1", retroactive=False)


	dataColl1 = my_onto.logDataCollection("D1", "U1", "T1", "R1")
	dataColl2 = my_onto.logDataCollection("D2", "U1", "T0", "R3")

	da1 = my_onto.logDataAccess(dataColl1, "T1", "R1")

	my_onto.reason()


	my_onto.save("testonto.owl")


def mainWithArgparse():

	parser = argparse.ArgumentParser()

	#creates new ontology at iri if True, loads one if False
	parser.add_argument("-l", "-load", nargs=2, help='loads ontology: iri load new', metavar='')
	#default - if doesnt exist, create
	#--new

	#creates a consent: D,U, T, R, nameofConsent, retroactivity(True,False)
	parser.add_argument("-c", "--consent", nargs=6, help='creates consent: D U T R consentName isRetroactive', metavar='')
	#creates a withdrawal: D,U, T, R, nameofConsent, retroactivity(True,False)
	parser.add_argument("-w", "--withdrawal", nargs=6, help='creates withdrawal: D U T R withdrawalName isRetroactive', metavar='')
	#creates a data collection at D, U, T, R
	parser.add_argument("-C", "--dataCollection", nargs=4, help="logs data collection: D U T R", metavar='')
	#creates a dataAccess at dc object, T, R
	parser.add_argument("-a", "--dataAccess", nargs=3, help='logs data access: dataCollectionObject T R', metavar='')
	
	#make automatic...
	#would need name 
	#saves with given file name
	parser.add_argument("-s", nargs=1, help='saves file at given name', metavar='')
	#runs reasoner
	parser.add_argument("-r", "--reasoner", action='store_true', help='runs reasoner')


	args = parser.parse_args()

	my_onto = None

	#loads ontology if True, creates new if false
	if args.l[1] == "True":
		my_onto = OWLgenerator(args.l[0], create_new=True)
		my_onto.baseForTest()
	else:
		my_onto = OWLgenerator(args.l[0], create_new=False)

	#if consent/withdrawal is retroactive
	retroC = False
	retroW = False

	#creates withdrawal
	if args.withdrawal != None:
		#checks retroactivity
		if args.withdrawal[5] == "True":
			retroW = True

		my_onto.userWithdrawal(args.withdrawal[0], args.withdrawal[1], args.withdrawal[2], args.withdrawal[3], args.withdrawal[4], retroW)

	#creates consent
	if args.consent != None:
		#checks retroactivity
		if args.consent[5] == "True":
			retroC = True

		my_onto.userConsent(args.consent[0], args.consent[1], args.consent[2], args.consent[3], args.consent[4], retroC)

	#creates data collection
	if args.dataCollection != None:
		my_onto.logDataCollection(args.dataCollection[0], args.dataCollection[1], args.dataCollection[2], args.dataCollection[3])
	
	#creates data access
	if args.dataAccess != None:
		dc = my_onto.getDataCollection(args.dataAccess[0])
		my_onto.logDataAccess(dc, args.dataAccess[1], args.dataAccess[2])

	#saves file
	if args.s != None:
		my_onto.save(args.s[0])

	if args.reasoner:
		my_onto.reason()



if __name__ == "__main__":
	mainWithArgparse()
