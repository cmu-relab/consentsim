# Consent Simulation Framework

The consent simulation framework is used to simulate events concerning the granting and withdrawl or consent, and the collection and access of data. The framework is written in python and consists of two components:

* consent_model.py: the consent model component is used to build an initial consent model and to perform sequenced operations on the model, including granting and withdrawing consent, and collecting and accessing data.

* simulator.py: the simulator component is used to read simulation scenario scipts and to perform the scripted operations on a given consent model.

## Usage

1. Create an initial consent model, which contains an unrefined data and recipient hierarchy:
./consent_model.py init.owl

2. After creating the initial consent model, the model user can load the init.owl file into Protege and refine the Data and Recipient classes by adding sub-classes and defining disjoint relationships among these classes. The refined OWL file can then be saved as a base.owl model for manipulation using scripted scenarios.

3. Simulate a scripted consent scenario:
./simulator.py base.owl script/scenario.simple models/simple.owl

4. After running the scenario, the model user can load the simple.owl model into Protege to inspect and query the model.

## Scenario Language

Scenarios are written using a simple event language. Each event description consists of a command word, followed by one or more arguments. Arguments may be optional words, separated by vertical bars, or variables in angular brackets. Variables include concepts and individuals in the knowledge base. Optional arguments appear in square brackets.

### Variables

The following variables may appear in the language:

* <DATA> is any sub-concept of the Data concept, or the Data concept, which is the class of data that can be collected or accessed.

* <DATASUBJECT> is an individual in the DataSubject concept, which is person about whom data is collected and accessed.

* <RECIPIENT> is any sub-concpt of the Recipient concept, or the Recipient concept, representing by whom data is collected.

* <CONSENT> is an individual in the Consent concept, which is used to grant and revoke consent.

* <COLLECT-START> is a sub-concept of the Time concept, which denotes the start of a time interval. If ommitted, it will be the current time step.

* <COLLECT-STOP> is a sub-concept of the Time concept, which denotes the end of a time interval. If ommitted, it will be one time step beyond the collection start by default.

* <ACCESS-START> is a sub-concept of the Time concept, which denotes the start of a time interval. If ommitted, it will be the current time step.

* <ACCESS-STOP> is a sub-concept of the Time concept, which denotes the end of a time interval. If ommitted, it will be one time step beyond the access start by default.

### Event Descriptions

The following event descriptions can be expressed in the language:

The grant command is used to grant consent by a data subject for a recipient to collect and access data. If the retro argument is supplied, this consent will be retroactive.

* grant [retro] <DATA> <DATASUBJECT> <RECIPIENT> :<CONSENT>
* Ex. grant Location datasubject1 Advertiser :consent1

The withdraw command is used to withdraw a previously granted consent.

* withdraw [retro] :<CONSENT>
* Ex. withdraw retro :consent1

The collect command is used to express a collection event at the current time step on a given class of data for a data subject by the given recipient.

* collect <DATA> <DATASUBJECT> <RECIPIENT>
* Ex. collect PreciseLocation datasubject1 Advertiser

The access command is used to express an access event at the current time step on a given class of data for a data subject by the given recipient. If the collection start and stop times are provided, then the access will reference data collected in that interval. Otherwise, the current time step is assumed.

* access <DATA> <DATASUBJECT> <RECIPIENT> [<COLLECT-START> [<COLLECT-STOP>]]
* Ex. access PreciseLocation datasubject1 Advertiser T2

The assume command is used to test whether a collection or access event is authorized by a given consent. The first argument indicates whether the scenario author believes this event should be authorized (true) or unauthorized (false). The remainder of the arguments correspond to a collection and access event description. In addition, however, the author can write time intervals to test events in the past.

* assume true|false collect <DATA> <DATASUBJECT> <RECIPIENT> [<COLLECT-START> [<COLLCT-STOP>]]

* assume true|false access <DATA> <DATASUBJECT> <RECIPIENT> [<COLLECT-START> [<COLLCT-STOP> [<ACCESS-START> [<ACCESS-STOP>]]]]]

### Simulation Parameters

Tests, expressed using the assume command, generate temporary queries that are not saved in the output OWL file. To save these queries for later inspection, the scenrio author can set the simulation parameter 'destroy_queries' to false, before expressing the queries, and later reset the parameter to true after the desired queries are saved to the output.

* set destroy_queries false|true
* Ex. set destroy_queries false

### Comments

Any line that begins with a pound sign will be ignored by the simulator.
