# Python VM Deployment Tool

A Python-based VMware vCenter automation tool that deploys virtual machines by cloning templates using YAML configuration files. Built with PyVmomi for seamless vSphere integration.

## Overview

This tool automates the deployment of virtual machines in VMware vSphere environments by:
- Reading VM specifications from YAML configuration files
- Connecting to vCenter Server using PyVmomi
- Cloning VMs from existing templates
- Configuring network settings with static IP addresses
- Customizing Linux guest OS settings
- Powering on VMs automatically after deployment

## Features

- **Template-based deployment**: Clone VMs from existing templates
- **Network customization**: Configure static IP addresses, gateways, and DNS
- **Hardware specification**: Define CPU, memory, and disk requirements
- **Idempotent operations**: Safe to run multiple times (existing VMs will cause vCenter errors)
- **Environment-based authentication**: Secure password handling via environment variables
- **SSL flexibility**: Option to disable certificate validation for development environments
- **Real-time logging**: Progress updates with emoji indicators

## Prerequisites

- Python 3.6 or higher
- VMware vCenter Server access
- Existing VM templates in vCenter
- Network connectivity to vCenter Server
- Appropriate permissions in vSphere (VM creation, template access, datastore access)

## Installation

1. Clone or download the project files
2. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Set your vCenter password as an environment variable for security:
```bash
export VCENTER_PASSWORD='your_vcenter_password'
```

### YAML Configuration File

The deployment is configured via YAML files. See `configs/deploy.yml` for the structure:

```yaml
vcenter:
  host: 10.11.4.73                           # vCenter Server IP/FQDN
  username: Administrator@vsphere.local       # vCenter username
  password_env: VCENTER_PASSWORD              # Environment variable name
  validate_certs: false                       # SSL certificate validation

vms:
  - name: websrv-01                          # VM name (must be unique)
    template: Ubuntu-20                       # Source template name
    datacenter: Datacenter                    # Target datacenter
    cluster: cluster1                         # Target cluster
    datastore: datastore1                     # Target datastore
    hardware:                                 # Hardware specifications
      cpu: 2                                  # Number of vCPUs
      memory_mb: 4096                         # Memory in MB
      disk_gb: 40                             # Disk size in GB
    network:                                  # Network configuration
      name: VLAN_100                          # Port group name
      ip: 10.11.4.100                         # Static IP address
      netmask: 255.255.255.0                  # Subnet mask
      gateway: 10.11.4.1                      # Default gateway
      dns:                                    # DNS servers
        - 8.8.8.8
        - 8.8.4.4
```

#### Configuration Parameters

**vCenter Section:**
- `host`: vCenter Server hostname or IP address
- `username`: vCenter authentication username
- `password_env`: Name of environment variable containing password
- `validate_certs`: Boolean to enable/disable SSL certificate validation

**VM Section:**
- `name`: Unique name for the new VM
- `template`: Name of the source template in vCenter
- `datacenter`: Target datacenter name
- `cluster`: Target cluster name  
- `datastore`: Target datastore name
- `hardware`: Hardware resource allocation
- `network`: Network configuration with static IP settings

## Usage

### Basic Deployment

Deploy VMs using a configuration file:
```bash
python deploy_vm.py configs/deploy.yml
```

### Multiple VM Deployment

Add multiple VM definitions to the `vms` array in your YAML file:
```yaml
vms:
  - name: websrv-01
    template: Ubuntu-20
    # ... configuration
  - name: websrv-02  
    template: Ubuntu-20
    # ... configuration
  - name: dbsrv-01
    template: CentOS-8
    # ... configuration
```

### Custom Configuration Files

Create custom YAML files for different environments:
```bash
python deploy_vm.py configs/production.yml
python deploy_vm.py configs/development.yml
python deploy_vm.py configs/testing.yml
```

## File Structure

```
project/
├── deploy_vm.py          # Main deployment script
├── requirements.txt      # Python dependencies
├── README.md            # This documentation
└── configs/
    └── deploy.yml       # Sample configuration file
```

## Dependencies

- **pyvmomi**: VMware vSphere API Python bindings
- **PyYAML**: YAML file parsing library

## Error Handling

The script includes error handling for common scenarios:

- **Invalid credentials**: Authentication failures are caught and reported
- **Missing environment variables**: Script exits with clear error message
- **Duplicate VM names**: vCenter will raise an error if VM name already exists
- **Missing vCenter objects**: Script validates that templates, datacenters, clusters, and datastores exist

## Security Considerations

- **Password storage**: Never hardcode passwords in configuration files
- **Environment variables**: Use environment variables for sensitive credentials
- **SSL validation**: Enable certificate validation in production environments
- **Access control**: Ensure proper vSphere permissions are configured

## Logging and Output

The script provides real-time feedback with emoji indicators:
- 🔗 Connection established
- 🔧 VM cloning in progress  
- ✅ Successful deployment
- ❌ Error conditions

All output goes to STDOUT. Redirect to a file if logging is required:
```bash
python deploy_vm.py configs/deploy.yml > deployment.log 2>&1
```

## Troubleshooting

**Connection Issues:**
- Verify vCenter host and credentials
- Check network connectivity
- Confirm SSL settings match your environment

**Template Issues:**
- Ensure template exists and is accessible
- Verify template has proper guest OS configuration
- Check template permissions

**Resource Issues:**
- Confirm sufficient resources in target cluster
- Verify datastore has adequate space
- Check resource pool permissions

**Network Issues:**
- Validate port group exists and is accessible
- Confirm IP address is available and in correct range
- Verify DNS and gateway configuration

## Limitations

- Currently supports Linux guest OS customization only
- Requires pre-existing templates
- Static IP configuration only (no DHCP support)
- Single network adapter per VM
- Limited hardware customization options

## Development Notes

This project was developed as part of Project 3 for Cybersécurité 1A coursework. The script is designed to be idempotent and safe for educational environments.

## License

Educational use only. Please refer to your institution's policies regarding code distribution and usage.