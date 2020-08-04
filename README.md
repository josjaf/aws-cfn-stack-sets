# AWS CFN Stack Sets

* This library is meant to help you define Stack Sets and deploy them across your Organization
* This code is meant to be run in the Organization Master Account
* The Organization Master Account is the only account that has access to the Child Accounts and the Organization API
* There are two kinds of ways of deploying Stack Sets - Service and Account level. This code provides examples of each
* The advantage of deploying to Organization Units (OUs) is that the Stack Sets can be automatically added and removed when accounts move through OUs
* In Order to target Ous, you must trust the Stack Set Service in the Organization Master Account. 
    * `aws organizations enable-all-features`
    * `aws organizations enable-aws-service-access --service-principal member.org.stacksets.cloudformation.amazonaws.com`
    * List of Serice Principals: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrated-services-list.html
    * see `prep_org.py` for enabling in python
## Examples Provided
* See `stack_set_helpers/stack_set_data.py`

* Edit line 36 on Stack Set Data `trusted_account_id = Org_helpers.get_id_account_by_name(self.session, 'joshlab')` this will deploy a role to the whole Organization that trusts an account named `joshlab`
* If you do not edit this line, the code will fail


## Running the code
* `export PYTHONPATH=$(pwd)`
* `python3 create_stack_set.py`

# Notes
* Switching from `OrganizationAccountAccessRole` in the children requires deploying `AWSCloudFormationStackSetExecutionRole.yml` in all of the children, see `deploy_child_stackset_role.py` for doing this across the Organization
* `deploy_child_stackset_role.py` can also be used to deploy a CloudFormation stack to the entire Organization without using Stack Sets. 