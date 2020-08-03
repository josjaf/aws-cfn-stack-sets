# AWS CFN Stack Sets
* This library is meant to help you define Stack Sets and deploy them across your Organization
* This code is meant to be run in the Organization Master Account
* The Organization Master Account is the only account that has access to the Child Accounts and the Organization API

## Examples Provide
* See `stack_set_helpers/stack_set_data`
* Edit line 36 on Stack Set Data `trusted_account_id = Org_helpers.get_id_account_by_name(self.session, 'joshlab')`