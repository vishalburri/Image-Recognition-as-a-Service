import boto3
import time
import datetime

ec2 = boto3.resource('ec2', region_name='us-east-1')
ec2_client = boto3.client('ec2', region_name='us-east-1')
sqs = boto3.client('sqs', region_name='us-east-1')
cloudwatch = boto3.client('cloudwatch')
ami_id = 'ami-0c0d32b5bbf7c12f2'
security_group_ids = ['sg-05220ab67d3789415', 'sg-03ab8519900f1ec06']
instance_type = 't2.micro'
iam_instance_profile = {
    'Name': 'ec2auto-scaler-role'}
user_data = '''#!/bin/bash
sudo -u ubuntu sh -c "cd /home/ubuntu/Image-Recognition-as-a-Service/app-tier  && git pull && cp ../../imagenet-labels.json . && python3 app.py"
'''
key_pair_name = 'CSE-546-project1'
MAX_INSTANCES = 19


def launch_ec2_instances(num_instances):
    try:
        instances = ec2.create_instances(
            ImageId=ami_id,
            MinCount=num_instances,
            MaxCount=num_instances,
            InstanceType=instance_type,
            SecurityGroupIds=security_group_ids,
            IamInstanceProfile={
                'Arn': 'arn:aws:iam::376277702783:instance-profile/ec2auto-scaler-role'
            },
            UserData=user_data,
            KeyName=key_pair_name,
        )
        current_running_count = len(get_instances_by_state())
        for instance in instances:
            current_running_count += 1
            ec2.create_tags(Resources=[instance.id], Tags=[
                {
                    'Key': 'Name',
                    'Value': "app-instance-" + str(current_running_count),
                },
            ])

        instance_ids = [instance.id for instance in instances]

        print(
            f"Created {len(instance_ids)} EC2 instances with IDs: {', '.join(instance_ids)}")
    except Exception as e:
        print(e)


def scale_out_ec2():
    num_of_messages = get_approximate_messages_visible_from_queue()
    running_instances = len(get_instances_by_state())
    pending_instances = len(get_instances_by_state(['pending']))
    stopping_instances = len(get_instances_by_state(['shutting-down']))
    total_instances = running_instances + pending_instances
    if (num_of_messages == 0 and (running_instances + pending_instances) > 1):
        response = ec2_client.describe_instances(
            Filters=[{'Name': 'image-id', 'Values': [ami_id]}])
        instances = response['Reservations'][0]['Instances']
        tag_name = ''
        terminate_list = []
        for instance in instances:
            print(instance['InstanceId'])
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        tag_name = tag['Value']
                        print(tag_name)
                        if tag_name != 'app-instance-1':
                            terminate_list.append(instance['InstanceId'])
        ec2_client.terminate_instances(InstanceIds=terminate_list)

    if (pending_instances > 0 or num_of_messages == 0):
        print(
            f"{num_of_messages} messages: Returning no messages or pending instances available")
        return
    if (running_instances >= MAX_INSTANCES or pending_instances >= MAX_INSTANCES or (running_instances + pending_instances) >= MAX_INSTANCES):
        print("MAX limit reached")
        return

    if (stopping_instances > 0):
        print("Stopping instances are present.. returning")

    if total_instances < num_of_messages:
        print(
            f"Total Ins: {total_instances}, num of messages : {num_of_messages}")
        num_instances_required = min(
            num_of_messages - total_instances, MAX_INSTANCES - total_instances)
        launch_ec2_instances(num_instances_required)


def get_approximate_messages_from_queue() -> int:
    response = sqs.get_queue_attributes(QueueUrl='https://sqs.us-east-1.amazonaws.com/376277702783/CSE-546-project1-request-queue', AttributeNames=[
        'ApproximateNumberOfMessages'])
    num_of_messages = response['Attributes']['ApproximateNumberOfMessages']
    return int(num_of_messages)


def get_approximate_messages_visible_from_queue() -> int:
    try:
        start_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        end_time = datetime.datetime.utcnow()

        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/SQS',
            MetricName='ApproximateNumberOfMessagesVisible',
            Dimensions=[
                {
                    'Name': 'QueueName',
                    'Value': 'CSE-546-project1-request-queue'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Maximum']
        )
        if len(response['Datapoints']) > 0:
            num_messages = response['Datapoints'][-1]['Maximum']
            return num_messages
        else:
            return 0
    except Exception as e:
        print(e)


def get_instances_by_state(state=None):
    if state is None:
        state = ['running']
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': state
        },
        {
            'Name': 'image-id',
            'Values': [ami_id]
        }
    ]
    instances = ec2.instances.filter(Filters=filters)
    return [instance.id for instance in instances]


def auto_scale():
    while True:
        scale_out_ec2()
        time.sleep(10)
