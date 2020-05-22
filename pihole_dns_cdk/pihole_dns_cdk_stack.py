from aws_cdk import (
    aws_ec2,
    aws_ecs,
    aws_logs,
    aws_ecs_patterns,
    aws_elasticloadbalancingv2 as aws_elb,
    core
)

class PiholeDnsCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create a VPC in 3 AZs
        vpc = aws_ec2.Vpc(
            self, 'dns_vpc',
            max_azs = 3
        )

        # add vpc flowlog for easier debugging
        vpc.add_flow_log(
            "flowlog"
        )

        # create the ecs cluster
        cluster = aws_ecs.Cluster(
            self, 'ecs_cluster',
            vpc = vpc
        )

        # add ec2 cluster capacity and maximum spot price
        cluster.add_capacity("spot_group",
            instance_type = aws_ec2.InstanceType("t3.nano"),
            spot_price = '0.005',
            spot_instance_draining = True
        )

        # create a network load balancer
        nlb = aws_elb.NetworkLoadBalancer(self, "public_nlb",
            vpc = vpc,
            internet_facing = True,
        )

        task_def = aws_ecs.Ec2TaskDefinition(self, "task_def")

        container = task_def.add_container("container",
            memory_limit_mib = 128,
            image = aws_ecs.ContainerImage.from_registry("pihole/pihole")
        )

        # add the ec2 service with a public nlb
        ec2_service = aws_ecs.Ec2Service(self, "pihole_service",
            cluster = cluster,
            desired_count = 1,
            task_definition = task_def
        )

        # add internal security group
        ec2_service.cluster.connections.allow_from(other = aws_ec2.Peer.ipv4(vpc.vpc_cidr_block), port_range = aws_ec2.Port.all_tcp())
        ec2_service.cluster.connections.allow_from(other = aws_ec2.Peer.ipv4(vpc.vpc_cidr_block), port_range = aws_ec2.Port.all_udp())


        '''
        # add container udp mapping
        container_53_udp    = aws_ecs.PortMapping(
            container_port  = 53,
            protocol        = aws_ecs.Protocol.UDP)

        ec2_service.task_definition.default_container.add_port_mappings(container_53_udp)

        '''
        container_53_tcp    = aws_ecs.PortMapping(
            container_port  = 53,
            protocol        = aws_ecs.Protocol.TCP)

        ec2_service.task_definition.default_container.add_port_mappings(container_53_tcp)

        container_80_tcp    = aws_ecs.PortMapping(
            container_port  = 80,
            protocol        = aws_ecs.Protocol.TCP)

        ec2_service.task_definition.default_container.add_port_mappings(container_80_tcp)

        # create a target group and add the tcp health check
        udp_tg = aws_elb.NetworkTargetGroup(
            self,
            target_type = aws_elb.TargetType.INSTANCE,
            id = "tcp53",
            port = 53,
            vpc = vpc
        )

        ec2_service.attach_to_network_target_group(udp_tg)

        # add the tcp/53 listener
        list_udp = nlb.add_listener(
            id = "list-udp",
            protocol = aws_elb.Protocol.TCP,
            port = 53,
            default_target_groups = [udp_tg]
        )

        # register the listener
        udp_tg.register_listener(list_udp)

        # create a target group and add the tcp health check
        tcp_tg = aws_elb.NetworkTargetGroup(
            self,
            target_type = aws_elb.TargetType.INSTANCE,
            id = "tcp80",
            port = 80,
            vpc = vpc
        )

        ec2_service.attach_to_network_target_group(tcp_tg)

        # add the tcp/80 listener
        list_tcp = nlb.add_listener(
            id = "listtcp",
            protocol = aws_elb.Protocol.TCP,
            port = 80,
            default_target_groups = [tcp_tg]
        )

        # register the listener
        udp_tg.register_listener(list_tcp)

        # print the loadbalanacer dns name
        core.CfnOutput(
            self, "load_balancer_dns",
            value = nlb.load_balancer_dns_name
        )
