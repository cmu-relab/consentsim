# consentsim
Policy evolution with consent simulation

## Simulation Design

**Research Questions:**
* ?

### Operations
1. User: Consent to, Withdraw consent
2. System: Collect data from user, Access data for purpose

### Realism
**Users:** Users are sampled from a demographic pool. The PEW Social Media Fact Sheet shows percent of U.S. adults who use social media. The 2019 U.S. Census estimates show total U.S. adults in multi-demographic groups (e.g., number of black females aged 25-29 with a college education), which can be combined with PEW to estimate the demographic pool.

**Events:**
* Account creation yields user demographic data.
* State model to account for user engagement with online service.
* Model changes that trigger withdrawal operations for specific demographic groups:
  * New retroactive consent to collect sensitive data
  * New non-retroactive consent to collect sensitive data
