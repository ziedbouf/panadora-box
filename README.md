# panadora box

The project is inspired from kqueen developed by mirantis with slight difference on supporting different kubernetes 
deployement. Also, the solutions will provides similair compoents to banzaicloud out of the box to support entreprises.


However, Panadora includes difference in the adopted stacks to help support different use cases:

## Panadora vs Kqueen
- Postgres first: Kqueen using etcd as the data store to keep track of different metadata. For panadora box, we adopt postgres as the main data store to keep track of all needed information to deploy and build stacks on the top of panadora deployment
- Flask-restplus: Kqueen api are build using native flask view to generate all the needed api for the system. Panadora box adopt flask-restplus with all the batery included
- KOPS: Kqueen provision only cluster for openstacks, aks and gke. In Panadora, we opt for using thrid party project to provision clusters based on user platform of choice. We include kops to support :
  - google compute engine
  - aws elastic compute
  - openstack 
  - Vmware
- Wave ekscli: To support eks
- Google google-cloud-python client: To support gke

## Panadora vs Banzaicloud 

For we will try to adopt different ideas from banzaicloud including:
- Vault for secret management 
- Dex for authentification  
- Velero for cluster backup
- Istio for service mesh 
- Grafana and prometheus for logging 
- Anchor for vulenerability scan 

However the difference will include using jenkins-x as main solution for CI/CD.



