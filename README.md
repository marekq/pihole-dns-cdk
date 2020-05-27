pihole-dns-cdk
==============

Create your own Pihole DNS service hosted on Fargate. The solution uses an EC2 instance that's automatically provisioned in an autoscaling group. In order to lower cost, spot instances will be used in the future and Elastic IP's are used instead of a Network Load Balancer or the Global Accelerator. You can deploy the stack to AWS using the CDK easily. 

WARNING: The security groups for the solution are currently set open to the Internet and will be restricted later - be mindful of this while developing and testing the setup. Do not use this deployment in production accounts and monitor for bandwidth costs carefully. 


Roadmap
-------

- [ ] Restrict security group IP's to your home address or a given subnet. 
- [ ] Test Lambda function to remap Elastic IP thoroughly. 
- [ ] Add spot instance hosting option to lower cost. 
- [ ] Output Pihole logging to a central location (i.e. S3). 


Contact
-------

In case you have any suggestions, questions or remarks, please raise an issue or reach out to @marekq.
