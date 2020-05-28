from aws_cdk import (
    aws_autoscaling,
    aws_ec2,
    aws_lambda,
    aws_logs,
    core
)

import boto3, random, requests, string

class PiholeDnsCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # get the local ip address to whitelist
        whitelist_ip = requests.get("https://ipinfo.io/ip").text.strip('\n') + "/32"

        # create a VPC in all AZs
        vpc = aws_ec2.Vpc(
            self, 'dns_vpc',
            max_azs = 10,
            nat_gateways = 0,
            subnet_configuration = [
                aws_ec2.SubnetConfiguration(
                    name = "publicSubnet", subnet_type = aws_ec2.SubnetType.PUBLIC)
            ]
        )

        # add vpc flowlog for easier debugging
        vpc.add_flow_log(
            "flowlog"
        )

        # add user data to ec2 instance
        user_data = aws_ec2.UserData.for_linux()

        # add ec2 instance user data from file
        def get_userdata():
            with open('ec2/boot.sh', 'r') as userdata:
                return userdata.read().replace("@PASSWORD@", pihole_passw)    

        # generate a random pihole web ui password
        pihole_passw = ''.join(random.choice(string.ascii_lowercase) for i in range(10))

        # set the password in userdata with the generated one
        user_data.add_commands(get_userdata())

        # create the ec2 instance
        ec2 = aws_ec2.Instance(
            self, "pihole-ec2",
            vpc = vpc,
            instance_type = aws_ec2.InstanceType('t3a.nano'),
            machine_image = aws_ec2.AmazonLinuxImage(generation = aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            vpc_subnets = {'subnet_type': aws_ec2.SubnetType.PUBLIC},
            key_name = "workbook",
            user_data = aws_ec2.UserData.custom(get_userdata())
        )
        
        
        # tag the ec2 instance 
        core.Tag.add(ec2, "stack", "pihole")

        # set the password as an ec2 instance tag
        core.Tag.add(ec2, "PiholePassword", pihole_passw)

        # add the pihole admin panel password as an ec2 instance tag
        # this way it can be randomly generated and doesn't require you to ssh into the instance to retrieve

        # create security group with inbound access from the internet
        sg = aws_ec2.SecurityGroup(
            self, "allow_dns_http_world",
            description = 'Allow ssh from world',
            vpc = vpc
        )

        # add tcp/22 security group rule
        sg.add_ingress_rule(
            aws_ec2.Peer.ipv4(whitelist_ip), aws_ec2.Port.tcp(22)
        )

        # add tcp/80 security group rule
        sg.add_ingress_rule(
            aws_ec2.Peer.ipv4(whitelist_ip), aws_ec2.Port.tcp(80)
        )

        # add udp/53 security group rule
        sg.add_ingress_rule(
            aws_ec2.Peer.ipv4(whitelist_ip), aws_ec2.Port.udp(53)
        )

        # attach security group to instance
        ec2.add_security_group(sg)

        # create elastic ip
        eip = aws_ec2.CfnEIP(self, 'elastic-ip', 
            domain = 'vpc', 
            instance_id = ec2.instance_id
        )

        '''
        # get the elastic ip address of the ec2 instance
        client = boto3.client('ec2')

        addr_dict = client.describe_addresses(AllocationIds = [eip.attr_allocation_id])
        elastic_ip = addr_dict['Addresses'][0]['PublicIp']

        # print the elastic ip allocation id
        core.CfnOutput(
            self, "elastic_allocation_id",
            value = eip.attr_allocation_id
        )
        '''

        # print the pihole web ui password
        core.CfnOutput(
            self, "pihole_web_ui_password",
            value = pihole_passw
        )

        # print the whitelisted ip in the ec2 security group
        core.CfnOutput(
            self, "whitelisted_ip",
            value = whitelist_ip
        )

        '''
        # print the elastic ip of the ec2 instance
        # you can set this ip address as your dns server over udp/53 and access the pihole web ui over tcp/80
        core.CfnOutput(
            self, "public_elastic_ip",
            value = elastic_ip
        )
        '''
