import boto3
from stack_set_helpers import helpers, cfn_helpers, iam_helpers, org_helpers
import multiprocessing
from multiprocessing import Process
import logging

Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()
Iam_helpers = iam_helpers.IamHelpers()
Org_helpers = org_helpers.Organization_Helpers()

def deploy(child_session, stack_name, AdministratorAccountId, failed_accounts, account):
    try:
        # TODO Check whether this role exists in a cfn stack
        # TODO if the role exists, check if the trust relationship is correct
        if Iam_helpers.check_iam_role_exists(child_session,
                                             'AWSCloudFormationStackSetExecutionRoleQS') and not Cfn_helpers.cfn_check_stack_exists(
            child_session, stack_name):
            msg = 'AWSCloudFormationStackSetExecutionRoleQS role exists in child account, but is managed outside aws-cfn-stack-sets, free to continue, assuming Admin Role has access to child accounts'
            print(msg)
            return msg

        response = Cfn_helpers. \
            create_update_stack(child_session,
                                dict(StackName=stack_name,
                                     TemplateBody=Helpers.file_to_string('templates/AWSCloudFormationStackSetExecutionRole.yml'),
                                     #TemplateURL='https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetExecutionRole.yml',
                                     Parameters=Cfn_helpers.dict_to_cfn_parameters(
                                         {'AdministratorAccountId': AdministratorAccountId})

                                     )

                                )
        print(response)
        response = Cfn_helpers.stack_complete(child_session, stack_name)
    except Exception as e:
        print(e)
        failed_accounts.append(account)

    return


def main():
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)


    org_session = boto3.session.Session(profile_name='orgmaster')
    org_accounts = Org_helpers.get_org_accounts(org_session)

    shared_session = boto3.session.Session()
    sts = shared_session.client('sts')
    AdministratorAccountId = sts.get_caller_identity()['Account']
    print(f"AdministratorAccountId: {AdministratorAccountId}")

    procs = []
    global failed_accounts
    failed_accounts = []
    stack_name = 'aws-cfn-stack-sets-child'
    for account in org_accounts:
        child_session = Helpers.get_child_session(account, 'OrganizationAccountAccessRole', org_session)
        proc = Process(target=deploy, args=(child_session, stack_name, AdministratorAccountId, failed_accounts, account))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()
        #deploy(child_session, stack_name, AdministratorAccountId, failed_accounts, account)



    return


if __name__ == '__main__':
    main()
