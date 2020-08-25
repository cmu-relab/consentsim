# Consent Simulation Framework

The consent simulation framework is used to simulate events concerning the granting and withdrawl or consent, and the collection and access of data. The framework is written in python and consists of two components:

* consent_model.py: the consent model component is used to build an initial consent model and to perform sequenced operations on the model, including granting and withdrawing consent, and collecting and accessing data.

* simulator.py: the simulator component is used to read simulation scenario scipts and to perform the scripted operations on a given consent model.

## Usage

1. Create an initial consent model, which contains an unrefined data and recipient hierarchy:
./consent_model.py init.owl --init

2. After creating the initial consent model, the model user can load the init.owl file into Protege and refine the Data and Recipient classes by adding sub-classes and defining disjoint relationships among these classes. The refined OWL file can then be saved as a base.owl model for manipulation using scripted scenarios.

3. Simulate a scripted consent scenario:
./simulator.py base.owl script/scenario.simple models/simple.owl

After running the scenario, the model user can load the simple.owl model into Protege to inspect and query the model.
