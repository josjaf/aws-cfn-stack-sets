"""
run from the org master account
"""

import os
import uuid
import boto3

import multiprocessing
from multiprocessing import Process
import logging

import stack_set_helpers.stack_set_constants as stack_set_constants
from stack_set_helpers import helpers, cfn_helpers, org_helpers

shared_session = boto3.session.Session()
Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()
Org_helpers = org_helpers.Organization_Helpers()


def stack_set_deploy(stack_set_deploy_definition, shared_session):
    """
    create / update stack set with waiter
    :param stack_sets_boundary:
    :param shared_session:
    :return:
    """

    deploy = True
    create_update = True
    cfn = shared_session.client('cloudformation')
    definition = stack_set_deploy_definition

    # try, catch operation in progress error and keep running
    try:
        stack_set_name = definition['StackSet']['StackSetName']
        Helpers.print_separator(f"Deploying StackSet: {definition['StackSet']['StackSetName']}")

        if not Cfn_helpers.stack_set_exists_check(shared_session, definition['StackSet']['StackSetName']):
            print(f"Stack Set: {definition['StackSet']['StackSetName']} CREATING")
            if create_update:
                operation_response = cfn.create_stack_set(**definition['StackSet'])
                print(f"Operation Response: {operation_response}")
                # Cfn_helpers.operation_id_waiter(session=shared_session,
                #                                 stack_name=definition['StackSet']['StackSetName'],
                #                                 operation_response=operation_response)
            if deploy:
                Cfn_helpers.stack_set_waiter(shared_session, stack_set_name)
                print(f"Creating Stack Instances: {stack_set_name}")
                response = cfn.create_stack_instances(**definition['InstanceArgs'])
                print(response)
                Cfn_helpers.stack_set_waiter(shared_session, stack_set_name)

        else:
            print(f"Stack Set: {definition['StackSet']['StackSetName']} UPDATING")
            # print(definition)
            if create_update:
                Cfn_helpers.stack_set_waiter(shared_session, stack_set_name)
                operation_response = cfn.update_stack_set(**definition['StackSet'])
                print(f"Operation Response: {operation_response}")
                # Cfn_helpers.operation_id_waiter(session=shared_session,
                #                                 stack_name=definition['StackSet']['StackSetName'],
                #                                 operation_response=operation_response)
            if deploy:
                # Cfn_helpers.operation_id_waiter(shared_session, stack_set_name, response)
                Cfn_helpers.stack_set_waiter(shared_session, stack_set_name)
                response = cfn.update_stack_instances(**definition['InstanceArgs'])
                print(f"Updating Stack Instances: {stack_set_name}")
                Cfn_helpers.stack_set_waiter(shared_session, stack_set_name)


    except Exception as e:
        print(e)
        raise e
    return


def main():
    StackSetConstants = stack_set_constants.StackSetConstants
    session = boto3.session.Session()
    sts = session.client('sts')
    account_id = sts.get_caller_identity()['Account']
    org_accounts = Org_helpers.get_org_accounts(session)

    procs = []
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    stack_sets = [
        {'TemplateBody': Helpers.file_to_string('templates/role.yml'), 'StackSetName': 'aws-cfn-stack-sets-child1',
         'Description': 'Role1'},
        {'TemplateBody': Helpers.file_to_string('templates/role.yml'), 'StackSetName': 'aws-cfn-stack-sets-child2',
         'Description': 'Role2'}, ]

    # TODO WRAP IN FUNCTION
    for stack_set in stack_sets:
        stack_set_arg = StackSetConstants.create_stack_set_args
        stack_set_arg['StackSetName'] = stack_set['StackSetName']
        stack_set_arg['TemplateBody'] = stack_set['TemplateBody']
        stack_set_arg['Description'] = stack_set['Description']
        parameters = {'SharedAccountId': account_id}
        parameters = Cfn_helpers.dict_to_cfn_parameters(parameters)
        stack_set_arg['Parameters'] = parameters  # should be a list of dictionaries

        stack_set_instance_args = StackSetConstants.instaces_dict
        stack_set_instance_args['StackSetName'] = stack_set_arg['StackSetName']
        stack_set_instance_args['Accounts'] = org_accounts
        stack_set_instance_args['OperationId'] = str(uuid.uuid1())

        stack_set_deploy_definition = {
            'StackSet': stack_set_arg,
            'InstanceArgs': stack_set_instance_args,
            'region': 'us-east-1',
        }

        shared_session_thread = boto3.session.Session()
        proc = Process(target=stack_set_deploy, args=(stack_set_deploy_definition, shared_session_thread))
        procs.append(proc)
        proc.start()
    # wait for threads to finish
    for proc in procs:
        proc.join()


if __name__ == '__main__':
    main()
