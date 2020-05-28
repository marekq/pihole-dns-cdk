pihole-dns-cdk
==============

Create your own Pihole DNS service hosted on Fargate. The solution uses an EC2 instance that's automatically provisioned in an autoscaling group. 


Installation
------------


You can deploy the stack to AWS using the CDK easily. Run 'cdk deploy' in the root of the folder to start the process. 


Considerations
--------------


Elastic IP's are used instead to expose the instance of a Network Load Balancer or the Global Accelerator in order to lower static cost to a minimum. Running the solution should cost ~$4/month for the on-demand t3.nano instance that is deployed plus some additional costs for bandwidth and CloudWatch logging. You can lower cost additionally by using a Savings Plan commitment. If it's feasible, spot instances may be used in the future to lower cost even further, but this may be a bit too much over engineering and cause other issues.  


Roadmap
-------

- [ ] Add spot instance hosting option to lower cost (if feasible, currently seems complex). 
- [ ] If using spot instances, test Lambda function to remap Elastic IP thoroughly. 
- [X] Restrict security group IP's to your home address or a given subnet. 


Contact
-------

In case you have any suggestions, questions or remarks, please raise an issue or reach out to @marekq.

