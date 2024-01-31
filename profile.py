"""A cluster of r7525 nodes, attached to a LAN
"""

import geni.portal as portal
import geni.rspec.pg as rspec

imageList = [
    ('urn:publicid:IDN+clemson.cloudlab.us+image+praxis-PG0:ubuntu2204-doca2.2.0', 'UBUNTU 22.04 DOCA 2.2.0'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU22-64-STD', 'UBUNTU 22.04'),
]

pc = portal.Context()
pc.defineParameter("num_nodes", "Number of GPU nodes",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("os_image", "OS image",
                   portal.ParameterType.IMAGE, imageList[0], imageList)
pc.defineParameter("data_size", "local storage size",
                   portal.ParameterType.STRING, "512GB")
params = pc.bindParameters()

request = pc.makeRequestRSpec()

# add lan
lan = request.LAN("Lan")
lan.best_effort = True
lan.vlan_tagging = True
lan.link_multiplexing = True

# add bluefield for r7525 hw type
global linkbf
linkbf = request.Link('bluefield')
linkbf.type = "generic_100g"

# normal nodes
for i in range(params.num_nodes):
    node = request.RawPC("node{}".format(i + 1))
    node.disk_image = params.os_image
    node.hardware_type = 'r7525'
    bs = node.Blockstore("bs{}".format(i + 1), "/data")
    bs.size = params.data_size
    intf = node.addInterface("if1")
    # r7525 requires special config to use its normal 25Gbps experimental network
    intf.bandwidth = 25600
    # Initialize BlueField DPU.
    bfif = node.addInterface("bf")
    bfif.addAddress(rspec.IPv4Address(
        "192.168.10.{}".format(i + 1), "255.255.255.0"))
    bfif.bandwidth = 100000000
    linkbf.addInterface(bfif)
    intf.addAddress(rspec.IPv4Address(
        "192.168.1.{}".format(i + 1), "255.255.255.0"))
    lan.addInterface(intf)

pc.printRequestRSpec(request)
