import boto3
import boto3.ec2
import time
#install aws-cli from https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html
#run aws configure to create the files

def main():
    instance_id = 'i-04be3c11f60f40e31'
    ec2 = boto3.client('ec2')
    #response = ec2.start_instances(InstanceIds=["i-0e7acdea36be2e3aa"], DryRun=False)
    ssm_client = boto3.client('ssm')  # use region code in which you are working
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands': [
                'echo \"hello world\"'
            ]
        }
    )
    time.sleep(1)
    command_id = response['Command']['CommandId']
    output = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id,
    )
    print(output['StandardOutputContent'])
    #response = ec2.stop_instances(InstanceIds=["i-0e7acdea36be2e3aa"], DryRun=False)


main()
