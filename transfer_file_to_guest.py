import ssl
import requests
import time
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def find_vm_by_id(content, vm_id):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in container.view:
        if vm._moId == vm_id:
            container.Destroy()
            return vm
    container.Destroy()
    return None

def upload_file_to_vm(vcenter, user, pwd, vm_id, guest_user, guest_pwd, local_file_path, remote_file_path):
    # Disable SSL certificate verification
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE

    try:
        # Connect to vCenter
        si = SmartConnect(host=vcenter, user=user, pwd=pwd, sslContext=context)
        content = si.RetrieveContent()

        # Find the VM by ID
        vm = find_vm_by_id(content, vm_id)
        if not vm:
            raise Exception(f"VM with ID {vm_id} not found.")

        # Create guest authentication
        creds = vim.vm.guest.NamePasswordAuthentication(username=guest_user, password=guest_pwd)

        # Initiate file manager
        file_manager = content.guestOperationsManager.fileManager

        # Check if the VM is powered on
        if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
            raise Exception(f"VM with ID {vm_id} is not powered on.")

        # Get file size
        with open(local_file_path, 'rb') as file_data:
            file_size = len(file_data.read())
            file_data.seek(0)

            # Initiate file transfer
            url = file_manager.Initiat
