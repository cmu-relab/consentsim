#!env/bin/python3

import argparse, types, os
from owlready2 import *

class ConsentModel:
    
    def __init__(self, onto):
        self.onto = onto
        self.next_access = 1
        self.next_collection = 1
        self.next_consent = 1
        self.this_time = 1
        self.destroy_queries = True
        self.next_query = 1
        
        for i in onto.Access.instances():
            x = int(i.name[1:])
            if x > self.next_access:
                self.next_access = x + 1
        for i in onto.Collection.instances():
            x = int(i.name[1:])
            if x > self.next_collection:
                self.next_collection = x + 1
        for i in onto.Consent.instances():
            x = int(i.name[7:])
            if x > self.next_consent:
                self.next_consent = x + 1
        for i in onto.DataSubject.instances():
            x = int(i.name[12:])
            if x > self.next_data_subject:
                self.next_data_subject = x + 1
        for i in onto.Time.subclasses():
            x = int(i.name[1:])
            if x > self.this_time:
                self.this_time = x

    @classmethod
    def init(cls, iri):
        onto = get_ontology(iri)

        with onto:
            class Time(Thing):
                pass
            class T1(Time):
                pass
            class T2(T1):
                pass
            class Consent(Thing):
                pass
            class ConsentSet(Thing):
                pass
            class Data(Thing):
               pass
            class DataSubject(Thing):
                pass
            class Recipient(Thing):
                pass
            class Access(Thing):
                pass
            class Collection(Thing):
                pass
            class AllDisjoint(Access, Collection):
                pass
            class accessedBy(Data >> Recipient):
                pass
            class accessedAt(Data >> Time):
                pass
            class collectedBy(Data >> Recipient):
                pass
            class collectedAt(Data >> Time):
                pass
            class about(Data >> DataSubject):
                pass
            class authorizes(Consent >> Data):
                pass
            class authorizedBy(ObjectProperty):
                inverse_property = authorizes
        return cls(onto)

    @classmethod
    def load(cls, iri):
        onto = get_ontology(iri).load()
        return cls(onto)

    def earliestStartTime(self):
        return self.onto.T1
    
    def currentTime(self):
        return self.onto['T%i' % self.this_time]

    def nextTime(self, time=None):
        if not time:
            time = self.currentTime()
        next_time = int(time.__name__[1:]) + 1
        while self.this_time + 1 < next_time:
            self.step()
        return self.onto['T%i' % next_time]

    def getTime(self, time_name):
        if int(time_name[1:]) <= self.this_time:
            return self.onto[time_name]
        return None

    def createData(self, class_name, super_class_name='Data'):
        super_class = None
        for cls in self.onto.classes():
            if 'base.%s' % super_class_name == str(cls):
                super_class = cls
                break
        if not super_class:
            super_class = types.new_class(super_class_name, (self.onto.Data,))

        sub_class = None
        for cls in self.onto.classes():
            if 'base.%s' % class_name == str(cls):
                sub_class = cls
                break
        if not sub_class:
            sub_class = types.new_class(class_name, (super_class,))
            
        if not super_class in sub_class.is_a:
            sub_class.is_a.append(super_class)
            
        return sub_class
    
    def createDataSubject(self, indiv_name):
        return self.onto.DataSubject(indiv_name)

    def createRecipient(self, class_name):
        if class_name in globals():
            return globals()[class_name]
        
        return types.new_class(class_name, (self.onto.Recipient,))

    def step(self):
        self.this_time += 1
        current_time = self.currentTime()

        # create the next time
        next_time = types.new_class(
            'T%i' % (self.this_time + 1), (current_time,))

        # return the current time
        return current_time
        
    def grantConsent(self, data, data_subject, recipient,
                     retroactive=False):
        consent = self.onto.Consent('consent%i' % self.next_consent)
            
        # setup consent start times
        if retroactive:
            start_access = self.earliestStartTime()
        else:
            start_access = self.currentTime()
        start_collect = self.currentTime()

        # define consent data
        consent.is_a.append(
            self.onto.authorizes.only(
                data
            ))
        consent.is_a.append(
            self.onto.authorizes.only(
                self.onto.collectedBy.some(recipient)
                & self.onto.about.value(data_subject)
            ))
            
        # define collection and access start time
        consent.is_a.append(
            self.onto.authorizes.only(
                (
                    self.onto.Collection
                    & self.onto.collectedAt.some(start_collect)
                ) | (
                    self.onto.Access
                    & self.onto.collectedAt.some(start_collect)
                    & self.onto.accessedAt.some(start_access)
                )
            ))
        
        # add consent to consent equivalence set
        try:
            self.onto.ConsentSet.equivalent_to[0].instances.append(consent)
        except IndexError:    
            self.onto.ConsentSet.equivalent_to.append(OneOf([consent]))

        # housekeeping and return
        self.next_consent += 1
        return consent

    def withdrawConsent(self, consent, retroactive=False):
        # collection and access start time
        current_time = self.currentTime()
        if not retroactive:
            consent.is_a.append(
                Not(self.onto.authorizes.some(
                    (
                        self.onto.Collection
                        & self.onto.collectedAt.some(current_time)
                    ) | (
                        self.onto.Access
                        & self.onto.collectedAt.some(current_time)
                    )
                )
            ))
        else:
            consent.is_a.append(
                Not(self.onto.authorizes.some(
                    (
                        self.onto.Collection
                        & self.onto.collectedAt.some(current_time)
                    ) | (
                        self.onto.Access
                        & self.onto.collectedAt.some(current_time)
                    ) | (
                        self.onto.Access
                        & self.onto.accessedAt.some(current_time)
                    )
                )
            ))

    def collect(self, data, data_subject, collect_recipient):
        # set collection time
        collect_at = [self.currentTime(), self.nextTime()]
        
        # create collection event
        event = self.onto.Collection('c%i' % self.next_collection)
        event.is_a.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.collectedBy.some(collect_recipient)
            & self.onto.collectedAt.some(collect_at[0] & Not(collect_at[1]))
        )

        # housekeeping and return
        self.next_collection += 1
        return event

    def access(self, data, data_subject, collect_recipient,
               collect_at=[None, None]):
        # set collection time, if unspecified
        if not collect_at[0]:
            collect_at[0] = self.currentTime()
        if not collect_at[1]:
            collect_at[1] = self.nextTime(collect_at[0])

        # set access time
        access_at = [self.currentTime(), self.nextTime()]

        # create access event
        event = self.onto.Access('a%i' % self.next_access)
        event.is_a.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.accessedAt.some(access_at[0] & Not(access_at[1]))
            & self.onto.collectedBy.some(collect_recipient)
            & self.onto.collectedAt.some(collect_at[0] & Not(collect_at[1]))
        )

        # housekeeping and return
        self.next_access += 1
        return event

    def isCollectable(self, data, data_subject,
                      collect_recipient, collect_at=[None, None]):
        # set collection time, if unspecified
        if not collect_at[0]:
            collect_at[0] = self.currentTime()
        if not collect_at[1]:
            collect_at[1] = self.nextTime(collect_at[0])

        # create query
        query = types.new_class(
            'query%i' % self.next_query, (self.onto.Collection,))
        query.equivalent_to.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.collectedBy.some(collect_recipient)
            & self.onto.collectedAt.some(collect_at[0] & Not(collect_at[1]))
            & self.onto.authorizedBy.some(self.onto.ConsentSet)
        )

        # test query in knowledgebase
        sync_reasoner()
        result = Nothing in query.equivalent_to

        # housekeeping and return
        if self.destroy_queries:
            destroy_entity(query)
        index = self.next_query
        self.next_query += 1
        return index, not result

    def isAccessible(self, data, data_subject,
            collect_recipient, collect_at=[None, None],
                     access_at=[None, None]):

        # set collection time, if unspecified
        if not collect_at[0]:
            collect_at[0] = self.currentTime()
        if not collect_at[1]:
            collect_at[1] = self.nextTime(collect_at[0])
        # set access time, if unspecified
        if not access_at[0]:
            access_at[0] = self.currentTime()
        if not access_at[1]:
            access_at[1] = self.nextTime(access_at[0])

        # create query
        query = types.new_class(
            'query%i' % self.next_query, (self.onto.Access,))
        query.equivalent_to.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.collectedBy.some(collect_recipient)
            & self.onto.collectedAt.some(collect_at[0] & Not(collect_at[1]))
            & self.onto.accessedAt.some(access_at[0] & Not(access_at[1]))
            & self.onto.authorizedBy.some(self.onto.ConsentSet)
        )

        # test query in knowledgebase
        sync_reasoner()
        result = Nothing in query.equivalent_to

        # housekeeping and return
        if self.destroy_queries:
            destroy_entity(query)
        index = self.next_query
        self.next_query += 1
        return index, not result

    def save(self, filename):
        with open(filename, 'wb') as f:
            self.onto.save(file=f, format='rdfxml')

def main(argv):
    parser = argparse.ArgumentParser(
        description='Generate a consent model')
    parser.add_argument(
        'owl_file', type=str,
        help='OWL file to save new consent model')
    parser.add_argument(
        '--namespace', type=str, default='https://relab.cs.cmu.edu',
        help='namespace for class definitions')
    args = parser.parse_args()

    # initialize a new consent model
    model = ConsentModel.init(args.namespace)
    
    # save consent model to the given file
    model.save(args.owl_file)

if __name__ == "__main__":
    main(sys.argv[1:])
