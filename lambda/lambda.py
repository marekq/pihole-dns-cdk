import boto3

ec2 = boto3.client('ec2')

def check_ec2():
    x = ec2.describe_instances()
    print(x)

def handler(event, context):
    print(event)
    print(context)
    check_ec2()
