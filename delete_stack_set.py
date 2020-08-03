import boto3
import os
from stack_set_helpers import helpers, cfn_helpers, org_helpers
from botocore.exceptions import ClientError
import botocore
import uuid

import boto3
import threading

import time

Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()
Org_helpers = org_helpers.Organization_Helpers()


def delete_stack_set(session, stack_set, accounts):
    cfn = session.client('cloudformation')
    stack_set_name = stack_set['StackSetName']
    stack_set_response = cfn.describe_stack_set(
        StackSetName=stack_set_name
    )

    instances_dict = dict(StackSetName=stack_set_name,
                          # Accounts=accounts,
                          # DeploymentTargets={'OrganizationalUnitIds': [ou_id]},
                          Regions=[session.region_name],
                          RetainStacks=False,
                          OperationId=str(uuid.uuid1()))
    if 'OrganizationalUnitIds' in stack_set_response['StackSet']:
        instances_dict['DeploymentTargets'] = {
            'OrganizationalUnitIds': stack_set_response['StackSet']['OrganizationalUnitIds']}
    ### TODO if accounts

    try:
        print(f"Deleting Stack Set Instances for {stack_set_name}")
        organizations = session.client('organizations')
        # roots = [i['Id'] for i in organizations.list_roots()['Roots']]
        # ou_id = Org_helpers.get_ou_id_from_name(session, 'dev')
        response = cfn.delete_stack_instances(**instances_dict)
        print(response)
        inprogress = True
        while inprogress:
            try:
                response = cfn.delete_stack_set(
                    StackSetName=stack_set_name
                )
                inprogress = False
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'OperationInProgressException':
                    print(e.response['Error']['Code'])
                    inprogress = True
                    time.sleep(30)
            except Exception as e:
                raise e
        print(f"Operation Out of Progress")
        response = cfn.delete_stack_set(
            StackSetName=stack_set_name
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'StackSetNotFoundException':
            print(f"Stack Set Not Found: {stack_set_name}")
            response = cfn.delete_stack_set(
                StackSetName=stack_set_name
            )
            print(response)
        if 'Accounts list cannot be empty' in e.response['Error']['Message']:
            print(f"Stack Set Instance Empty: {stack_set_name}")
            response = cfn.delete_stack_set(
                StackSetName=stack_set_name
            )
            print(response)
        else:
            print(e)
    return


def main():
    shared_session = boto3.session.Session()
    shared_session = boto3.session.Session()

    org_session = boto3.session.Session()
    org_accounts = Org_helpers.get_org_accounts(org_session, remove_org_master=False)
    print(org_accounts)

    cfn = org_session.client('cloudformation')
    response = cfn.list_stack_sets(
        Status='ACTIVE'
    )
    stack_sets = [s for s in response['Summaries']]
    print(stack_sets)

    threads = []
    for stack_set in stack_sets:
        if stack_set['StackSetName'].startswith('AWS'):
            print(f"Skipping: {stack_set['StackSetName']}")
            continue
        print(f"Deleting {stack_set['StackSetName']}")
        # if stack_set['StackSetName'].startswith('iin-org-child-role'):
       # delete_stack_set(shared_session, stack_set, org_accounts)
        t = threading.Thread(target=delete_stack_set,
                             args=(shared_session, stack_set, org_accounts))
        # t = threading.Thread(target=worker, args=(account, session, results))
        threads.append(t)
        t.start()

    print(len(threads))
    for thread in threads:
        thread.join()

    return


if __name__ == '__main__':
    main()
