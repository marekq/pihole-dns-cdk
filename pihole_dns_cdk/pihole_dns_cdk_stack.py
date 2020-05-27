from aws_cdk import (
    aws_autoscaling,
    aws_ec2,
    aws_lambda,
    aws_logs,
    core
)

class PiholeDnsCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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

        '''
        yum install lighttpd-fastcgi php git
        '''


        # create the ec2 instance
        ec2 = aws_ec2.Instance(
            self, "pihole",
            vpc = vpc,
            instance_type = aws_ec2.InstanceType('t3.nano'),
            machine_image = aws_ec2.AmazonLinuxImage(generation = aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            vpc_subnets = {'subnet_type': aws_ec2.SubnetType.PUBLIC},
            key_name = "workbook"
        )
        
        # create security group with inbound access from the internet
        sg = aws_ec2.SecurityGroup(
            self, "allow_dns_http_world",
            description = 'Allow ssh from world',
            vpc = vpc
        )

        # add ssh
        sg.add_ingress_rule(
            peer = aws_ec2.Peer.any_ipv4(),
            connection = aws_ec2.Port.tcp(22)
        )

        # add tcp
        sg.add_ingress_rule(
            peer = aws_ec2.Peer.any_ipv4(),
            connection = aws_ec2.Port.tcp(80)
        )

        # add udp
        sg.add_ingress_rule(
            peer = aws_ec2.Peer.any_ipv4(),
            connection = aws_ec2.Port.udp(53)
        )

        # attach security group to instance
        ec2.add_security_group(sg)

        # create elastic ip
        eip = aws_ec2.CfnEIP(self, 'ElasticIP', 
            domain = 'vpc', 
            instance_id = ec2.instance_id
        )

        # create lambda function to update Elastic IP every minute
        eip_func = aws_lambda.Function(self, 'eip-lambda', 
            code = aws_lambda.Code.asset('lambda'),
            runtime = aws_lambda.Runtime.PYTHON_3_8,
            handler = "handler",
            timeout = core.Duration.seconds(10),
            tracing = aws_lambda.Tracing.ACTIVE,
            environment = {
                "eip_alloc": eip.attr_allocation_id
            }
        )

        core.CfnOutput(
            self, "elastic_allocation_id",
            value = eip.attr_allocation_id
        )

