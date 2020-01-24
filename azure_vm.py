from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from secrets import az_client_id, az_secret, az_tenant, az_subscription_id

credentials = ServicePrincipalCredentials(
    client_id = az_client_id,
    secret = az_secret,
    tenant = az_tenant
)

subscription_id = az_subscription_id

compute_client = ComputeManagementClient(credentials, subscription_id)
resource_group_name = 'cloud'
vm_name = 'Noico'

def start_vm(compute_client):
    compute_client.virtual_machines.start(resource_group_name, vm_name)
def stop_vm(compute_client):
    compute_client.virtual_machines.deallocate(resource_group_name, vm_name)

#stop_vm(compute_client)
#start_vm(compute_client)
#input('Press enter to continue...')
# compute_client.virtual_machines.list_all()