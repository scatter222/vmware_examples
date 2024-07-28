import ssl
import requests
import time
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    container.Destroy()
    return obj

def upload_file_to_vm(vcenter, user, pwd, vm_name, guest_user, guest_pwd, local_file_path, remote_file_path):
    # Disable SSL certificate verification
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE

    try:
        # Connect to vCenter
        si = SmartConnect(host=vcenter, user=user, pwd=pwd, sslContext=context)
        content = si.RetrieveContent()

        # Find the VM
        vm = get_obj(content, [vim.VirtualMachine], vm_name)
        if not vm:
            raise Exception(f"VM {vm_name} not found.")

        # Create guest authentication
        creds = vim.vm.guest.NamePasswordAuthentication(username=guest_user, password=guest_pwd)

        # Initiate file manager
        file_manager = content.guestOperationsManager.fileManager

        # Initiate guest operations manager
        guest_operations_manager = content.guestOperationsManager

        # Check if the VM is powered on
        if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
            raise Exception(f"VM {vm_name} is not powered on.")

        # Upload the file
        with open(local_file_path, 'rb') as file_data:
            file_size = len(file_data.read())
        
        file_data.seek(0)

        url = file_manager.InitiateFileTransferToGuest(vm, creds, remote_file_path, vim.vm.guest.FileManager.FileTransferInformation(),
                                                       file_size, overwrite=True)
        response = requests.put(url, data=file_data, verify=False)
        
        if response.status_code == 200:
            print(f"File {local_file_path} uploaded successfully to {remote_file_path}")
        else:
            raise Exception(f"Failed to upload file. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        Disconnect(si)

# Example usage
vcenter = "your_vcenter_server"
user = "your_username"
pwd = "your_password"
vm_name = "your_vm_name"
guest_user = "guest_username"
guest_pwd = "guest_password"
local_file_path = "/path/to/local/file"
remote_file_path = "/path/in/vm/filename"

upload_file_to_vm(vcenter, user, pwd, vm_name, guest_user, guest_pwd, local_file_path, remote_file_path)
