import boto3
import os
from stack_set_helpers import helpers, cfn_helpers, org_helpers, stack_set_constants as stack_set_constants
import botocore
import uuid

Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()
Org_helpers = org_helpers.Organization_Helpers()

StackSetConstants = stack_set_constants.StackSetConstants()
org_session = boto3.session.Session()
organizations = org_session.client('organizations')
org_account_id = org_session.client('sts').get_caller_identity()['Account']


class StackSetDefinition():
    def __init__(self, stack_set_args, stack_set_instances, session):
        self.stack_set_args = stack_set_args
        self.stack_set_instances = stack_set_instances
        self.session = session
        print(self.stack_set_args['StackSetName'])




class StackSet_Dev():
    def __init__(self, *args, **kwargs):
        self.session = boto3.session.Session()
        self.stack_set_args = StackSetConstants.create_stack_set_args.copy()
        self.stack_set_args['StackSetName'] = 'iin-shared-dev'
        self.stack_set_args['TemplateBody'] = Helpers.file_to_string('templates/deploy_child_role_stack_set.yml')
        self.stack_set_args['Description'] = 'iin-bootstrap'
        self.stack_set_args['Parameters'] = Cfn_helpers.dict_to_cfn_parameters(
            {'namespace': 'iin', 'SharedAccountId': org_account_id, 'RoleName': 'iin-shared-dev'})
        self.stack_set_args['PermissionModel'] = 'SERVICE_MANAGED'
        self.stack_set_args['AutoDeployment'] = {'Enabled': True, 'RetainStacksOnAccountRemoval': False}

        self.stack_set_instances = StackSetConstants.instaces_dict.copy()
        self.stack_set_instances['StackSetName'] = self.stack_set_args['StackSetName']
        self.stack_set_args.pop('ExecutionRoleName')
        # stack_set_instance_args['Accounts'] = org_accounts
        # stack_set_instance_args['DeploymentTargets'] = {'OrganizationalUnitIds': [Org_helpers.get_principal_org_id(org_session)]}

        self.roots = [i['Id'] for i in organizations.list_roots()['Roots']]
        # ous = response = organizations.list_organizational_units_for_parent(
        #     ParentId=roots[0],
        # )
        self.stack_set_instances['DeploymentTargets'] = {
            'OrganizationalUnitIds': self.roots}

        self.ou_id = Org_helpers.get_ou_id_from_name(org_session, 'dev')

        self.stack_set_instances['DeploymentTargets'] = {
            'OrganizationalUnitIds': [self.ou_id]}
        self.stack_set_instances['OperationId'] = str(uuid.uuid1())
        return


class StackSet_Prod():
    def __init__(self, *args, **kwargs):
        self.session = boto3.session.Session()
        self.stack_set_args = StackSetConstants.create_stack_set_args.copy()
        self.stack_set_args['StackSetName'] = 'iin-shared-prod'
        self.stack_set_args['TemplateBody'] = Helpers.file_to_string('templates/deploy_child_role_stack_set.yml')
        self.stack_set_args['Description'] = 'iin-bootstrap'
        self.stack_set_args['Parameters'] = Cfn_helpers.dict_to_cfn_parameters(
            {'namespace': 'iin', 'SharedAccountId': org_account_id, 'RoleName': 'iin-shared-prod'})
        self.stack_set_args['PermissionModel'] = 'SERVICE_MANAGED'
        self.stack_set_args['AutoDeployment'] = {'Enabled': True, 'RetainStacksOnAccountRemoval': False}

        self.stack_set_instances = StackSetConstants.instaces_dict.copy()
        self.stack_set_instances['StackSetName'] = self.stack_set_args['StackSetName']
        self.stack_set_args.pop('ExecutionRoleName')
        self.roots = [i['Id'] for i in organizations.list_roots()['Roots']]

        self.stack_set_instances['DeploymentTargets'] = {
            'OrganizationalUnitIds': self.roots}

        self.ou_id = Org_helpers.get_ou_id_from_name(org_session, 'prod')

        self.stack_set_instances['DeploymentTargets'] = {
            'OrganizationalUnitIds': [self.ou_id]}
        self.stack_set_instances['OperationId'] = str(uuid.uuid1())



class StackSet_Org():
    def __init__(self, *args, **kwargs):


        self.session = boto3.session.Session()
        self.stack_set_args = StackSetConstants.create_stack_set_args.copy()
        self.stack_set_args['StackSetName'] = 'iin-org-child'
        self.stack_set_args['TemplateBody'] = Helpers.file_to_string('templates/deploy_child_role_stack_set.yml')
        self.stack_set_args['Description'] = 'Stack Set deployed from Pipeline'
        self.stack_set_args['Parameters'] = Cfn_helpers.dict_to_cfn_parameters(
            {'namespace': 'iin', 'SharedAccountId': org_account_id, 'RoleName': 'iin-org-child'})
        self.stack_set_args['PermissionModel'] = 'SERVICE_MANAGED'
        self.stack_set_args['AutoDeployment'] = {'Enabled': True, 'RetainStacksOnAccountRemoval': False}

        self.stack_set_instances = StackSetConstants.instaces_dict.copy()
        self.stack_set_instances['StackSetName'] = self.stack_set_args['StackSetName']
        self.stack_set_args.pop('ExecutionRoleName')
        # stack_set_instance_args['Accounts'] = org_accounts
        # stack_set_instance_args['DeploymentTargets'] = {'OrganizationalUnitIds': [Org_helpers.get_principal_org_id(org_session)]}

        self.roots = [i['Id'] for i in organizations.list_roots()['Roots']]
        # ous = response = organizations.list_organizational_units_for_parent(
        #     ParentId=roots[0],
        # )
        self.stack_set_instances['DeploymentTargets'] = {
            'OrganizationalUnitIds': self.roots}
        self.stack_set_instances['OperationId'] = str(uuid.uuid1())

        return

