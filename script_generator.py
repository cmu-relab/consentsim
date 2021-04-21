#!env/bin/python3

import sys, argparse, random, math


    
# script
class Script:

    def __init__(self):
        self.logs = []
    
    def log(self, event):
        print(event)
        self.logs.append(event)
    
    # save script on file
    def save(self, filename):
        with open(filename, 'w') as f:
            for line in self.logs:
                f.write(line+"\n")

    # advance one time step
    def step(self):
        self.log("step")
        
    # grant
    def grant(self, retro, data, data_subject, recipient, consent):
        self.log("grant "+("retro " if retro else "")+data+" "+data_subject+" "+recipient+" "+consent)
    
    # withdraw
    def withdraw(self, retro, consent):
        self.log("withdraw "+("retro " if retro else "")+consent)
    
    # collect
    def collect(self, data, data_subject, recipient):
        self.log("assume true collect "+data+" "+data_subject+" "+recipient)
        self.log("collect "+data+" "+data_subject+" "+recipient)
    
    # access
    def access(self, data, data_subject, recipient, on_collect_from=False, on_collect_to=False):
        time = ((on_collect_from+" "+on_collect_to if on_collect_to else on_collect_from) if on_collect_from else "")
        self.log("assume true access "+data+" "+data_subject+" "+recipient+" "+time)
        self.log("access "+data+" "+data_subject+" "+recipient+" "+time)
    
    # create new data
    def new_data(self, data, parent):
        self.log("new data "+data+" "+(parent if parent else "Data"))
    
    # create new recipient
    def new_recipient(self, recipient):
        self.log("new recipient "+recipient)
    
    # create new disjoint
    def new_disjoint(self, data1, data2):
        self.log("new disjoint "+data1+" "+data2)
    
    # create new eqiv
    def new_equiv(self, data1, data2):
        self.log("new eqiv "+data1+" "+data2)



# Database superclass
class Database:

    @staticmethod
    def get_one_randomly_in(list):
        if len(list) > 0: 
            # return list[ math.floor( len(list) * random.random() ) ]
            return random.choice(list)

    @classmethod
    def get_one_randomly(cls):
        return Database.get_one_randomly_in(cls.all)
    
    def __init__(self, name):
        childClass = self.__class__

        if not hasattr(childClass, 'id'):
            childClass.id = 0
        
        if not hasattr(childClass, 'all'):
            childClass.all = []
        
        self.name = name+str(childClass.id)
        childClass.id += 1
        childClass.all.append(self)



# Data
class Data(Database):

    # @classmethod
    # def get_one_randomly(cls):
    #     # if len(Data.all) > 0:
    #         return Data.all[ math.floor( len(Data.all) * random.random() ) ]

    def __init__(self, sibling, parent):
        Database.__init__(self, "Data")
        self.sibling = sibling
        if parent:
            self.parent = parent
            # self.granularity = self.parent.granularity + (1-self.parent.granularity)*0.5
            script.new_data(self.name, self.parent.name)
        else:
            self.parent = None
            # self.granularity = 0.1
            script.new_data(self.name, "Data")
        if sibling:
            script.new_disjoint(self.name, self.sibling.name)
        # Data.all.append(self)
            
    def specialize(self):
        self.parent = Data(self.sibling, self.parent)
        self.sibling = None
        # self.granularity += self.granularity*0.5
        script.new_data(self.name, self.parent.name)
        return self
    
    def diversify(self):
        return Data(sibling=self, parent=self.parent)
    
    def generalize(self):
        self.parent = self.parent.parent
        self.sibling = None # or self.parent.parent or self.parent.sibling
        script.new_data(self.name, self.parent.name)
        return self

# Data.id = 0
# Data.all = []



# Recipient
class Recipient:
    
    def __init__(self, reputation):
        Database.__init__(self, "Recipient")
        self.reputation = reputation
        script.new_recipient(self.name)
        Recipient.all.append(self)



# Policy
class Policy:

    def __init__(self, retro, data, recipient):
        self.retro = retro
        self.data = data
        self.recipient = recipient



# User
class DataSubject:

    granted_consents = {}

    def __init__(self, awareness):
        self.name = "datasubject"+str(DataSubject.id)
        DataSubject.id += 1
        self.awareness = awareness
        DataSubject.all.append(self)

    def granting_willingness(self, reputation):
        return 1-self.awareness + self.awareness * reputation
    
    def withdrawing_willingness(self, reputation):
        return 1 - (reputation)

DataSubject.id = 0
DataSubject.all = []



# Consent
class Consent(Database):

    @classmethod
    def get_collectibles(cls):
        collectible = []
        for c in cls.all:
            if c.collectible:
                collectible.append(c)
        return collectible

    @classmethod
    def get_one_collectible(cls):
        collectible = Consent.get_collectibles()
        return Database.get_one_randomly_in(collectible)

    @classmethod
    def get_accessibles(cls):
        accessible = []
        for c in cls.all:
            if c.accessible:
                accessible.append(c)
        return accessible

    @classmethod
    def get_one_accessible(cls):
        accessible = Consent.get_accessibles()
        return Database.get_one_randomly_in(accessible)

    def __init__(self, retro, data, data_subject, recipient):
        # Database.__init__(self, "consent")
        self.name = "consent" + str(Consent.id)
        Consent.id += 1
        self.retro = retro
        self.data = data
        self.data_subject = data_subject
        self.recipient = recipient

        self.withdrawn = False
        self.granted_at = step
        self.withdrawn_at = None

        self.collectible = True
        self.accessible = True

        self.access_from = step 
        self.access_to = None
        self.access_on_collected_from = 1 if retro else step
        self.access_on_collected_to = None

        script.grant(retro, self.data.name, self.data_subject.name, self.recipient.name, self.name)
        
        Consent.all.append(self)

    def withdraw(self, retro):
        script.withdraw(retro, self.name)

        self.withdrawn = True
        self.withdrawn_at = step

        self.collectible = False

        self.accessible = True if (not retro) & (self.withdrawn_at > self.granted_at) else False
        self.access_to = step if retro else None
        self.access_on_collected_to = step
    
Consent.id = 0
Consent.all = []



def generate(logging=True):
    # redirect standard error to the script_generation log
    # if logging:
    #     log = open('script_generation.log', 'w')
    #     stderr = sys.stderr
    #     sys.stderr = log

    global script
    script = Script()
    global step
    step = 1
    data_subject_creation_frequency = 0.1
    policy_creation_frequency = 0.1

    # root_data
    Data(None, None)

    while step < 200:

        # DataSubject
        if data_subject_creation_frequency >= random.random():
            DataSubject( awareness=random.random() )

        # grant
        if policy_creation_frequency >= random.random():
            # Policy
            policy = Policy(
                retro = random.random() >= 0.5,
                data = Data.get_one_randomly().diversify(), # script.new_data(data, parent)
                recipient = Recipient(
                    reputation = random.random()
                )
            )
            # grant
            for ds in DataSubject.all:
                if ds.granting_willingness(policy.recipient.reputation) > random.random():
                    consent = Consent(policy.retro, policy.data, ds, policy.recipient)

        # withdraw
        for c in Consent.all:
            if not c.withdrawn:
                reputation = c.recipient.reputation
                granted_for = step - c.granted_at
                if 1 - (reputation) > random.random():
                    c.withdraw(retro = random.random() >= 0.5)

        # collect data for each consent granted
        # collect_count = 0
        # for c in Consent.all:
        
        # collect at most 5 data randomly
        collectibles = Consent.get_collectibles()
        for i in range(2):
            if len(collectibles) > 0: 
                c = random.choice(collectibles)
                collectibles.remove(c)
                script.collect(c.data.name, c.data_subject.name, c.recipient.name)

        
        # access at most 5 data randomly
        accessibles = Consent.get_accessibles()
        for i in range(2):
            if len(accessibles) > 0: 
                c = random.choice(accessibles)
                accessibles.remove(c)
                if c.access_on_collected_to != None:
                    script.access(c.data.name, c.data_subject.name, c.recipient.name, "T"+str(c.access_on_collected_from), "T"+str(c.access_on_collected_to) )
                else:
                    script.access(c.data.name, c.data_subject.name, c.recipient.name, "T"+str(c.access_on_collected_from) )
        
        # access data under consent still granted
        # access_count = 0
        # for c in Consent.all:
        #     if c.accessible:
        #         access_count += 1
        #         if c.access_on_collected_to != None:
        #             script.access(c.data.name, c.data_subject.name, c.recipient.name, "T"+str(c.access_on_collected_from), "T"+str(c.access_on_collected_to) )
        #         else:
        #             script.access(c.data.name, c.data_subject.name, c.recipient.name, "T"+str(c.access_on_collected_from) )
        #     if access_count > 5:
        #         break

        # step
        step += 1
        script.step()

    script.save("scenario.generated")



def main(argv):
    parser = argparse.ArgumentParser(description='Simulate consent model events')
    # parser.add_argument('base_model', type=str,
    #                     help='the OWL file containing the base model')
    # parser.add_argument('script', type=str,
    #                     help='the simulation script describing a scenario')
    # parser.add_argument('ext_model', type=str, nargs='?',
    #                     help='the OWL file to save the simulation results')
    parser.add_argument('--nologging', action='store_true',
                        help='log standard error to simulation.log')
    args = parser.parse_args()

    generate( logging = args.nologging == False )
    
if __name__ == "__main__":
    main(sys.argv[1:])
