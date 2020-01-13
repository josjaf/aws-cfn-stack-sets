import boto3

from stack_set_helpers import helpers, cfn_helpers, iam_helpers

Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()
Iam_helpers = iam_helpers.IamHelpers()


def main():
    Helpers = helpers.Helpers()
    Cfn_helpers = cfn_helpers.CfnHelpers()
    Iam_helpers = iam_helpers.IamHelpers()
    session = boto3.session.Session()

    # deploy admin stack role
    stack = {}
    stack_name = 'aws-cfn-stack-sets-admin'
    stack['cfn_args'] = {'StackName': stack_name, 'Capabilities': ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                         'TemplateBody': Helpers.file_to_string(
                             'templates/AWSCloudFormationStackSetAdministrationRole.yml')}
    # 'TemplateURL': 'https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetAdministrationRole.yml'}

    # stack['cfn_args']['Parameters'] = Cfn_helpers.dict_to_cfn_parameters({''})
    if Iam_helpers.check_iam_role_exists(session,
                                         'AWSCloudFormationStackSetAdministrationRoleQS', ) and not Cfn_helpers.cfn_check_stack_exists(
        session, stack_name):
        msg = 'Admin role already exists, but created outside of aws-cfn-stack-sets, free to move on'
        print(msg)
        return  msg


    response = Cfn_helpers.create_update_stack(session, stack['cfn_args'])
    response = Cfn_helpers.stack_complete(session, stack['cfn_args']['StackName'])

    return


if __name__ == '__main__':
    main()
