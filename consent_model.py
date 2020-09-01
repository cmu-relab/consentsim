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
            class about(Data >> DataSubjet):
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
                    
    def current_time(self):
        return self.onto['T%i' % self.this_time]

    def earliest_start_time(self):
        return self.onto.T1

    def createData(self, class_name):
        if class_name in globals():
            return globals()[class_name]
        return types.new_class(class_name, (self.onto.Data,))
    
    def createDataSubject(self, indiv_name):
        return self.onto.DataSubject(indiv_name)

    def createRecipient(self, class_name):
        return types.new_class(class_name, (self.onto.Recipient,))

    def step(self):
        current_time = self.current_time()
        self.this_time += 1
        return types.new_class("T%i" % self.this_time, (current_time,))

    def next_time(self, time):
        next_time = 'T%i' % (int(time.__name__[1:]) + 1)
        while self.onto[next_time] == None:
            step = self.step()
        return self.onto[next_time]
        
    def grantConsent(self, data, data_subject, recipient, retroactive=False):
        consent = self.onto.Consent('consent%i' % self.next_consent)
            
        # setup consent start times
        if retroactive:
            start_access = self.earliest_start_time()
        else:
            start_access = self.current_time()
        start_collect = self.current_time()

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
        current_time = self.current_time()
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
                        & self.onto.accessedAt.some(current_time)
                    )
                )
            ))

    def collect(self, data, data_subject, recipient):
        start_time = self.current_time()
        stop_time = self.next_time(self.current_time())
        event = self.onto.Collection('c%i' % self.next_collection)
        event.is_a.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.collectedBy.some(recipient)
            & self.onto.collectedAt.some(start_time & Not(stop_time))
        )
        self.next_collection += 1
        return event

    def access(self, data, data_subject, recipient):
        start_time = self.current_time()
        stop_time = self.next_time(self.current_time())
        event = self.onto.Access('a%i' % self.next_access)
        event.is_a.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.accessedAt.some(start_time & Not(stop_time))
            & self.onto.accessedBy.some(recipient)
            & self.onto.collectedAt.some(start_time & Not(stop_time))
        )
        self.next_access += 1
        return event

    def isCollectable(self, data, data_subject, recipient):
        start_time = self.current_time()
        stop_time = self.next_time(self.current_time())
        query = types.new_class('query', (self.onto.Collection,))
        query.equivalent_to.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.collectedBy.some(recipient)
            & self.onto.collectedAt.some(start_time & Not(stop_time))
            & self.onto.authorizedBy.some(self.onto.ConsentSet)
        )
        sync_reasoner()
        result = Nothing in query.equivalent_to
        destroy_entity(query)
        return not result

    def isAccessible(self, data, data_subject, recipient):
        start_time = self.current_time()
        stop_time = self.next_time(self.current_time())
        query = types.new_class('query', (self.onto.Access,))
        query.equivalent_to.append(
            data
            & self.onto.about.value(data_subject)
            & self.onto.collectedBy.some(recipient)
            & self.onto.collectedAt.some(start_time & Not(stop_time))
            & self.onto.authorizedBy.some(self.onto.ConsentSet)
        )
        sync_reasoner()
        result = Nothing in query.equivalent_to        
        destroy_entity(query)
        return not result

    def save(self, filename):
        with open(filename, 'wb') as f:
            self.onto.save(file=f, format='rdfxml')

def scenario1(owl_file):
    model = ConsentModel.load('file://' + owl_file)
    ds = model.createDataSubject('datasubject1')
    data = model.createData('Location')
    advertiser = model.createRecipient('Advertiser')
    consent1 = model.grantConsent(data, ds, advertiser)
    model.step()
    consent2 = model.grantConsent(data, ds, advertiser, retroactive=False)
    model.step()
    model.withdrawConsent(consent1, retroactive=False)
    model.step()
    model.withdrawConsent(consent2, retroactive=True)
    model.save(owl_file)
    
def scenario2(owl_file):
    model = ConsentModel.load('file://' + owl_file)
    ds = model.createDataSubject('datasubject1')
    data = model.createData('Location')
    advertiser = model.createRecipient('Advertiser')
    consent1 = model.grantConsent(data, ds, advertiser)
    model.step()
    model.withdrawConsent(consent1, retroactive=False)
    model.step()
    consent2 = model.grantConsent(data, ds, advertiser, retroactive=False)
    model.step()
    model.withdrawConsent(consent2, retroactive=True)
    model.save(owl_file)
        
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
    model = ConsentModel.init(args.ns)

    # save consent model to the given file
    model.save(args.owl_file)

if __name__ == "__main__":
    main(sys.argv[1:])
