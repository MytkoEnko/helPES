from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
#from secrets import az_client_id, az_secret, az_tenant, az_subscription_id
import traceback

azure_variables = {
    'az_client_id' : '',
    'az_secret' : '',
    'az_tenant' : '',
    'az_subscription_id' : '',
    'az_group_name' : '',
    'az_vm_name' : ''
}


def azure_perform(action):
    '''Pass "start_vm" or "stop_vm" for actions'''
    credentials = ServicePrincipalCredentials(
        client_id=azure_variables['az_client_id'],
        secret=azure_variables['az_secret'],
        tenant=azure_variables['az_tenant']
    )

    subscription_id = azure_variables['az_subscription_id']

    compute_client = ComputeManagementClient(credentials, subscription_id)
    resource_group_name = azure_variables['az_group_name']
    vm_name = azure_variables['az_vm_name']
    if action == 'start_vm':
        compute_client.virtual_machines.start(resource_group_name, vm_name)
    if action == 'stop_vm':
        compute_client.virtual_machines.deallocate(resource_group_name, vm_name)
    if action == 'check_vm':
        try:
            response = compute_client.virtual_machines.get(resource_group_name, vm_name).as_dict()
            message = f'Name: {response["name"]}, \n' \
                      f'Type: {response["type"]}, \n' \
                      f'Location: {response["location"]}, \n' \
                      f'VM id: {response["vm_id"]},\n' \
                      f'Provisioning state: {response["provisioning_state"]}'
        except:
            message = 'Something went wrong, could\'t complete test\n' + traceback.format_exc()
        return message

# def start_vm(compute_client):
#     compute_client.virtual_machines.start(resource_group_name, vm_name)
# def stop_vm(compute_client):
#     compute_client.virtual_machines.deallocate(resource_group_name, vm_name)

#stop_vm(compute_client)
#start_vm(compute_client)
#input('Press enter to continue...')
# compute_client.virtual_machines.list_all()