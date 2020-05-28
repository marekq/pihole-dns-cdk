pihole-dns-cdk
==============

Create your own Pihole DNS service hosted on EC2 that can be deployed using the CDK. The solution uses an t3a.nano instance that's automatically provisioned in a public subnet. A security group is set that whitelists your IP address for HTTP and DNS access. 


Installation
------------


Run 'cdk deploy' in the root of the folder to start the process. Once the deployment has finished, you can retrieve the Elastic IP address and login password for the Pihole web gui. 

Pihole will automatically retrieve the standard block lists and use a local DNS resolver to retrieve DNS queries instead of a public one. You should not open up your DNS server or web service to the open Internet as the solution has not been tested for this. In addition, there could be vulnerabilities in either the DNS server, SSH server or HTTP server, which is why it is better to restrict access to these services. 


Considerations
--------------


Elastic IP's are used instead to expose the instance of a Network Load Balancer or the Global Accelerator in order to lower static cost to a minimum. Running the solution should cost ~$4/month for the on-demand t3a.nano instance that is deployed plus some additional costs for bandwidth and CloudWatch logging. You can lower cost additionally by using a Savings Plan commitment. If it's feasible, spot instances may be used in the future to lower cost even further, but this may be a bit too much over engineering and cause other issues.  


Roadmap
-------

- [ ] Add spot instance hosting option to lower cost (if feasible, currently seems complex). 
- [ ] If using spot instances, test Lambda function to remap Elastic IP thoroughly. 
- [X] Restrict security group IP's to your home address or a given subnet. 
- [X] Enable secure password generation for Pihole web interface.


Contact
-------

In case you have any suggestions, questions or remarks, please raise an issue or reach out to @marekq.

