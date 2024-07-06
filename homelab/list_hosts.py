from proxmoxer import ProxmoxAPI

HOMELAB_ADDRESS = ""
HOMELAB_LOGIN = ""
HOMELAB_PASS = ""

proxmox = ProxmoxAPI(
    HOMELAB_ADDRESS,
    user=HOMELAB_LOGIN,
    password=HOMELAB_PASS,
)
for node in proxmox.nodes.get():
    print("{0}:".format(node["node"]))
    for vm in proxmox.nodes(node["node"]).lxc.get():
        print(f"{vm['vmid']}. {vm['name']} => {vm['status']}")
