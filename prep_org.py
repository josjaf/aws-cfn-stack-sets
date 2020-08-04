import boto3
import botocore
import time


def main():
    session = boto3.session.Session()
    organizations = session.client('organizations')

    try:
        response = organizations.enable_all_features()
        print(response)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'HandshakeConstraintViolationException':
            pass
        else:
            raise e
    service_principals = ["member.org.stacksets.cloudformation.amazonaws.com", "ram.amazonaws.com", "compute-optimizer.amazonaws.com","tagpolicies.tag.amazonaws.com"]
    for service_principal in service_principals:
        print(f'Enabling Service Principal: {service_principal}')
        response = organizations.enable_aws_service_access(
            ServicePrincipal=service_principal
        )
        print(response)
    print(f"Sleeping for 60")
    time.sleep(60)
    return

if __name__ == '__main__':
    main()
    time.sleep(60)
    main()