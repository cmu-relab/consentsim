# consentsim
Policy evolution with consent simulation

## Simulation Design

**Research Questions:**
* Given a population response to a model change, how does policy scope and retroactivity affect participation?

### Operations
1. User: Consent to, Withdraw consent
2. System: Collect data from user, Access data for purpose, change policy

### Realism
**Users:** Users are sampled from a demographic pool. The PEW Social Media Fact Sheet shows percent of U.S. adults who use social media. The 2019 U.S. Census estimates show total U.S. adults in multi-demographic groups (e.g., number of black females aged 25-29 with a college education), which can be combined with PEW to estimate the demographic pool.

**Events:**
* Account creation yields user demographic data - how many users join the service per time interval
* Service usage - for each time interval, what proportions of users generate which kinds of information?
* Policy changes that trigger withdrawal operations for specific demographic groups:
  * New retroactive consent to collect sensitive data
  * New non-retroactive consent to collect sensitive data

### Simulation Design
* Simulation start - create initial policy setup, initial user base
* Simulation iteration (time step)
  - Register new users
  - Users generate data (system collects data)
  - System accesses data for specific purposes
  - After a number of iterations, scripted policy change event occurs and some users react (accept, withdrawal, do nothing)
* Simulation status / statistics
