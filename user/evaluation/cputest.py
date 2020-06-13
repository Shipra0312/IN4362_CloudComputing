import boto3
import numpy as np
import matplotlib.pyplot as plt
import datetime

instance_id = 'i-0e97f22a460630ba7'
client = boto3.client('cloudwatch')
ec2 = boto3.client('ec2')

response = ec2.monitor_instances(InstanceIds=[instance_id])
cpu = client.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': instance_id
        },
    ],
    StartTime=datetime.datetime(2020, 6, 13, 13, 48, 0),
    EndTime=datetime.datetime(2020, 6, 13, 13, 55, 0),
    Period=60,
    Statistics=[
        'Average',
        'Maximum',
    ],
    Unit='Percent'
)

average = np.mean(list(map(lambda x: x['Average'], cpu['Datapoints'])))
print(average)
