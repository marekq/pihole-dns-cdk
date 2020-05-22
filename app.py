#!/usr/bin/env python3

from aws_cdk import core

from pihole_dns_cdk.pihole_dns_cdk_stack import PiholeDnsCdkStack


app = core.App()
PiholeDnsCdkStack(app, "pihole-dns-cdk")

app.synth()
