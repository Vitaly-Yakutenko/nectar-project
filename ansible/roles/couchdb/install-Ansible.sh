#######################################################################
# GROUP 23
# CITY: Melbourne
# MEMBERS:
#  - Vitaly Yakutenko - 976504
#  - Shireen Hassan - 972461
#  - Himagna Erla - 975172
#  - Areeb Moin - 899193
#  - Syed Muhammad Dawer - 923859
#######################################################################

#Download and install Miniconda:
curl -OL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

#Check your Python version:
python --version

#Create a new virtual environment for Ansible:
conda create -n ansible-dev python=3

#Activate the new environment:
source activate ansible-dev

#Install Ansible:
pip install ansible

#Verify that the corresponding Python path is correct:
ansible --version

#Create a directory for Ansible configuration files and playbooks:
mkdir ~/ansible && cd ~/.ansible

#Create a configuration file and edit it to include the location where you will store your inventory file:
cat > /root/ansible/ansible.cfg << EOF
[defaults]
inventory = /root/ansible/hosts
EOF

#Create the inventory file with the public IP address or domain name of each of your nodes:
cat > /root/ansible/hosts << EOF
[dbserver]
couch1.cloudprojectnectar.co
couch2.cloudprojectnectar.co
EOF

#Test Inventory Groups, Use the all directive to ping all servers in your inventory:
ansible all -u root -m ping