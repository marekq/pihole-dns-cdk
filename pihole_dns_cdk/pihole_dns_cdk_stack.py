from aws_cdk import (
    aws_ec2,
    aws_ecs,
    aws_ecs_patterns,
    aws_elasticloadbalancingv2 as aws_elb,
    core
)

class PiholeDnsCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create a VPC in 1 AZ
        vpc = aws_ec2.Vpc(
            self, 'dns_vpc',
            max_azs = 1
        )

        # create the ecs cluster
        cluster = aws_ecs.Cluster(
            self, 'EC2',
            vpc = vpc
        )

        # add ec2 cluster capacity
        cluster.add_capacity("DefaultAutoScalingGroup",
            instance_type = aws_ec2.InstanceType("t3.nano"),
            spot_price = '0.005',
            spot_instance_draining = True
        )

        # add the fargate service with a public nlb
        ec2_service = aws_ecs_patterns.NetworkLoadBalancedEc2Service(
            self, "Pihole_Service",
            cluster = cluster,
            public_load_balancer = True,
            desired_count = 1,
            listener_port = 80,  
            memory_limit_mib = 128,
            task_image_options = {
                'image': aws_ecs.ContainerImage.from_registry("pihole/pihole"),
                'container_port': 80
            }
        )

        # add internal security group
        ec2_service.service.connections.allow_from(other = aws_ec2.Peer.ipv4(vpc.vpc_cidr_block), port_range = aws_ec2.Port.all_tcp())
        ec2_service.service.connections.allow_from(other = aws_ec2.Peer.ipv4(vpc.vpc_cidr_block), port_range = aws_ec2.Port.all_udp())

        # create a target group and add the tcp health check
        udp_tg = aws_elb.NetworkTargetGroup(
            self,
            target_type = aws_elb.TargetType.INSTANCE,
            id = "tg-udp",
            port = 53,
            vpc = vpc,
        )

        ec2_service.service.attach_to_network_target_group(udp_tg)

        # add the tcp/53 listener
        list_udp = ec2_service.load_balancer.add_listener(
            id = "list-udp",
            protocol = aws_elb.Protocol.TCP,
            port = 53,
            default_target_groups = [udp_tg]
        )

        # print the loadbalanacer dns name
        core.CfnOutput(
            self, "LoadBalancerDNS",
            value = ec2_service.load_balancer.load_balancer_dns_name
        )
