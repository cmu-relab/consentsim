#Simulation plan

#init method to set up the simulation - store necessary variables, read in contingency table, create owl generator
Init(contingency table, number of users to initialize to, number of runs, type(s) of policy changes, magnitude(s) of policy changes):
	#Create OWLGenerator
	#Read in contingency table (maybe want a separate method for that)
	#store population numbers in separate table, calculated off of contingency table
		# Initially perhaps have table n x m, with different age ranges and income levels. Each cell would contain the proportion of users in that intersection of age and income
		# Create a table of users with numbers calculated by initial number of users and the proportions in the table read in. numpy?
		# If want to have multiple tables, store in data structure we can expand into multiple separate tables
	#Num_users optionally input, stored
	#Many of these are ultimately based on what we end up doing with the contingency table.
	#Would need to store the time interval, initially at T0
	#Create ontology and add data types
	#stor var for num users created, so no overlaps? Or could update OWLGenerator

#creates the user data in the ontology; could be called in init, could be used in main to add new users to sim as it iterates
GenUserData(self - tables would already be stored, maybe pass in how many users to be added?):
	#Use OWLGenerator to create the user data in ontology
	#Create new users based on contingency table
	#would want to create consents for new users?

userConsent(self, maybe pass in the number of users/new consents that need to be created):
	# Use OWLGenerator to create consents for the users
	# single user or iterate through multiple users. Depends on where in the program user consents will be created
	# User names standardized - U#, so can easily iterate through users when necessary

CollectUserData(self):
	#use OWLGenerator to create data collection events for all users
	#I do not think it would matter about specific users

# use OWlGenerator to create data access events for users with appropriate consent
accessUserData(self):
	# check each user/ which users do not have consent conflicts for said time interval
	# Call checkConsent maybe
	# create data access for all appropriate users - maybe iterate through the list of users

#checks if user has consent. Can either be here or in OWLGenerator. Might want to put in OWLGenerator, so it is more flexable
checkConsent(self, maybe U, D, R to check for a specific consent, T depending on if is part of simulation.py or OWlGenerator):
	# Checks the user/data/time/recipient combination to be accessed has consent to be accessed. Might be tough to implement
	# Either pass in user or iterate through all the users, data types and recipients. Depends on how we use this I think

# actually creates the policy change event
#change the number of users and the demographics of the users 
PolicyChange(pass in the type of policy change, or maybe have that passed in in the init. How complex do we want to get with the policy changes in a single simulation?):
	# This would have to understand how the users change – how many users stop using, how many withdraw consent, and how this would affect the demographics
	# Perhaps have a new contingency table of how policy change affects the user demographics. multiply against previous user numbers table to get new demographics numbers, or could have a table that is multiplied directly with the number of users.
	# Store new table of users
	# Would this delete users from the ontology? Probably create another method to handle the deletions and update the ontology accordingly
	# How would we want to handle user consents/withdrawals with the users who leave?
	# Maybe want to create withdrawals for certain users because of the policy change - could be based on the policy change type
	
	# Possible policy changes: collecting more info, different purpose, share with a broader group. How would we want to represent these different changes, should we be able to alter how severe the changes are (maybe pass in a multiplier for severity, a key for the type of policy change)
	# Find the numbers we might want to use for each scenario?
	#somewhere store the contingency tables for the differnent policy changes, pass in those and a multiplyer to determine magnitude of policy change and its effect
	#use table multiplied against current user numbers to determine number of users quitting
	#after number of users leaving determined, use OWLGenerator to delete the users

#calculates the statistics of the policy changes
calcStats(self):
	Store the differences in each variation of the contingency tables.
	Have a stats method called at end of program, can calculate the types of changes between each table after policy changes
	Or could do calculations after each policy change, store them. Would need to store less contingency tables, depends on the stats we would want

	# store the change type, magnitude, number of users and their demographics who dropped
	# total number of users dropped

# A main method that would iterate through time intervals, update the ontology and user data, and simulate policy change.
main(self):
	# create the initial ontology with data types, recipients, initial users, T0. This sets everything up
	# A loop to iterate given number of times for simulation, Inside loop:
		# Each iteration in this loop would be a time interval, would start at T0
		# Call genUserData to add users that might join service
		# Do we want to create consents for each new user? Call userConsent to create consents for the new users
		# Call collectUser data to create dataCollection events for users in time step
		# Call accessUserData to create dataAccess events to create dataAccess events for the users, data types, and recipients
		# This would be where there may be issues with user consent - if they withdrew consent but data was accessed, the error should occur here? We probably would want to check in some capacity what violations might have occured
		# If on iteration number x, would want to simulate a privacy policy change. Call PolicyChange to update how users react to the change
		# Update time interval
		# Maybe don’t need to store time interval, can base it off of iteration number, I guess it depends on how the other methods use the time interval and if we would rather pass the interval number in each call or just have the methods check the stored variable. I guess I would rather store it as an attribute
	# After loop call the stats method to print simulation data to a csv file



	



#questions I thought of
#for the users that are added durring sim - do we want to imediatly create consents for them?
#do we keep or delete the data collection events for users who stopped using?
#should dataCollection events be created for each time interval?
#would the policy change delete users from the table
#do we want to keep or delete the data collections, accesses, consents, and withdrawals of the users who leave?

#Changes I would want to make to OWLGenerator:
	#add meathods to separately add and remove specific users to/from onotology
	#check if there are consent/withdrawal conflicts for certian U,D,T,R accesses
	#check for any privacy violations that have occured after data accesses
