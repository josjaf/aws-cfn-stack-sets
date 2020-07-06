import boto3
import os
from stack_set_helpers import helpers, cfn_helpers, org_helpers, stack_set_constants as stack_set_constants
import botocore
import uuid
import multiprocessing
import logging

Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()
Org_helpers = org_helpers.Organization_Helpers()
import stack_set_data

def stack_set_deploy(stack_set, shared_session):
    cfn = stack_set['Session'].client('cloudformation')
    # try, catch operation in progress error and keep running
    try:
        stack_set_name = stack_set['StackSet']['StackSetName']
        if not Cfn_helpers.stack_set_exists_check(stack_set['Session'], stack_set['StackSet']['StackSetName']):
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
            response = cfn.create_stack_set(**stack_set['StackSet'])
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
            response = cfn.create_stack_instances(**stack_set['InstanceArgs'])
            print(response)
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
        else:
            print(f"Found Stack Set: {stack_set['StackSet']['StackSetName']}")
            # print(value)
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
            response = cfn.update_stack_set(**stack_set['StackSet'])
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
            response = cfn.update_stack_instances(**stack_set['InstanceArgs'])
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
    except Exception as e:
        print(e)
        raise e
    # TODO FIX UPDATES
    # except botocore.exceptions.ClientError as e:
    #     if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
    # TODO Catch OperationInProgressException

    return
def main():

    SharedServicesDevStackSet = stack_set_data.ss_dev
    SharedServicesProdStackSet = stack_set_data.ss_prod
    OrgChildStackSet = stack_set_data.ss_org


    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    stack_sets = [
        {
            'StackSet': SharedServicesDevStackSet.stack_set_args,
            'InstanceArgs': SharedServicesDevStackSet.stack_set_instances,
            'region': 'us-east-1',
            'Session': SharedServicesDevStackSet.session
        },
        {
            'StackSet': OrgChildStackSet.stack_set_args,
            'InstanceArgs': OrgChildStackSet.stack_set_instances,
            'region': 'us-east-1',
            'Session': OrgChildStackSet.session
        },
        {
            'StackSet': SharedServicesProdStackSet.stack_set_args,
            'InstanceArgs': SharedServicesProdStackSet.stack_set_instances,
            'region': 'us-east-1',
            'Session': SharedServicesProdStackSet.session
        }

    ]
    print(stack_sets)
    # TODO CLEAN UP
    procs = []
    for stack_set in stack_sets:
        shared_session_thread = boto3.session.Session()
        proc = multiprocessing.Process(target=stack_set_deploy, args=(stack_set, shared_session_thread))
        procs.append(proc)
        proc.start()
        # wait for threads to finish
    for proc in procs:
        proc.join()





if __name__ == '__main__':
    main()
