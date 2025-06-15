import atexit
import ssl
import yaml
import os
import sys
from pyVim import connect
from pyVmomi import vim


def load_config(yaml_file):
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def clone_vm(si, vm_conf):
    content = si.RetrieveContent()
    template = get_obj(content, [vim.VirtualMachine], vm_conf['template'])
    datacenter = get_obj(content, [vim.Datacenter], vm_conf['datacenter'])
    cluster = get_obj(content, [vim.ClusterComputeResource], vm_conf['cluster'])
    datastore = get_obj(content, [vim.Datastore], vm_conf['datastore'])
    destfolder = datacenter.vmFolder
    resource_pool = cluster.resourcePool

    # Configure relocation spec
    relocationspec = vim.vm.RelocateSpec()
    relocationspec.datastore = datastore
    relocationspec.pool = resource_pool

    # Configure network settings
    nic = vm_conf['network']
    ip_spec = vim.vm.customization.IPSettings()
    ip_spec.ip = vim.vm.customization.FixedIp()
    ip_spec.ip.ipAddress = nic['ip']
    ip_spec.subnetMask = nic['netmask']
    ip_spec.gateway = [nic['gateway']]
    ip_spec.dnsServerList = nic.get('dns', [])

    adaptermap = vim.vm.customization.AdapterMapping()
    adaptermap.adapter = ip_spec

    globalip = vim.vm.customization.GlobalIPSettings()
    globalip.dnsServerList = nic.get('dns', [])

    ident = vim.vm.customization.LinuxPrep(
        hostName=vim.vm.customization.FixedName(name=vm_conf['name']),
        domain="localdomain"
    )

    customspec = vim.vm.customization.Specification()
    customspec.nicSettingMap = [adaptermap]
    customspec.globalIPSettings = globalip
    customspec.identity = ident

    # Clone specification
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relocationspec
    clonespec.customization = customspec
    clonespec.powerOn = True

    print(f"🔧 Cloning VM '{vm_conf['name']}' from template '{vm_conf['template']}'...")
    task = template.Clone(folder=destfolder, name=vm_conf['name'], spec=clonespec)
    wait_for_task(task)
    print(f"✅ VM '{vm_conf['name']}' deployed and powered on.")


def wait_for_task(task):
    from pyVim.task import WaitForTask
    return WaitForTask(task)


def main():
    if len(sys.argv) != 2:
        print("Usage: python deploy_vm.py <config.yml>")
        sys.exit(1)

    config_file = sys.argv[1]
    config = load_config(config_file)

    vc = config['vcenter']
    pwd = os.environ.get(vc['password_env'])

    if not pwd:
        print(f"❌ Environment variable '{vc['password_env']}' not set.")
        sys.exit(1)

    # Disable SSL cert verification if needed
    ctx = None
    if not vc.get('validate_certs', True):
        ctx = ssl._create_unverified_context()

    try:
        si = connect.SmartConnect(
            host=vc['host'],
            user=vc['username'],
            pwd=pwd,
            sslContext=ctx
        )
        atexit.register(connect.Disconnect, si)
        print("🔗 Connected to vCenter.")

        for vm in config['vms']:
            clone_vm(si, vm)

    except vim.fault.InvalidLogin:
        print("❌ Invalid login. Please check your username and password.")
        sys.exit(1)


if __name__ == "__main__":
    main()
