from stack_set_helpers import helpers, cfn_helpers, org_helpers

Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()
Org_helpers = org_helpers.Organization_Helpers()
from stack_set_helpers import stack_set_data
import botocore
import threading


def deploy_stack_set(stack_set):
    cfn = stack_set['Session'].client('cloudformation')
    # try, catch operation in progress error and keep running
    try:
        stack_set_name = stack_set['StackSet']['StackSetName']
        if not Cfn_helpers.stack_set_exists_check(stack_set['Session'], stack_set['StackSet']['StackSetName']):
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
            response = cfn.create_stack_set(**stack_set['StackSet'])
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
            response = Cfn_helpers.create_update_stack_instances(stack_set['Session'], stack_set['InstanceArgs'])
            print(response)
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
        else:
            print(f"Found Stack Set: {stack_set['StackSet']['StackSetName']}")
            # print(value)
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
            response = cfn.update_stack_set(**stack_set['StackSet'])
            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)

            response = Cfn_helpers.create_update_stack_instances(stack_set['Session'], stack_set['InstanceArgs'])
            # TODO WRITE CREATE UPDATE STACK SET INSTANCES

            Cfn_helpers.stack_set_waiter(stack_set['Session'], stack_set_name)
    except Exception as e:
        print(f"Caught exception with Stack Set: {stack_set['StackSet']['StackSetName']}")
        print(e)
        raise e
    # TODO FIX UPDATES
    # except botocore.exceptions.ClientError as e:
    #     if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
    # TODO Catch OperationInProgressException

    return


def main():
    IamOrgAdmin = stack_set_data.IamOrgAdmin()
    IamOrgAdmin_Accounts = stack_set_data.IamOrgAdmin_Accounts()
    # for new stack set, create new class in stack_set_data.py and instantiate the class here
    stack_sets = []
    for stack_set_definition in [IamOrgAdmin, IamOrgAdmin_Accounts]:  # reference new stack sets here

        dict_definition = {  # this may be a machine role
            'StackSet': stack_set_definition.stack_set_args,
            'InstanceArgs': stack_set_definition.stack_set_instances,
            'region': 'us-east-1',
            'Session': stack_set_definition.session
        }
        stack_sets.append(dict_definition)

    print(stack_sets)
    # TODO CLEAN UP

    threads = []
    for stack_set in stack_sets:
        t = threading.Thread(target=deploy_stack_set, args=(stack_set,))
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
