"""A cluster of r7525 nodes, attached to a LAN
"""

import geni.portal as portal
import geni.rspec.pg as rspec

imageList = [
    ('urn:publicid:IDN+clemson.cloudlab.us+image+praxis-PG0:ubuntu2204-doca2.2.0', 'UBUNTU 22.04 DOCA 2.2.0'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU22-64-STD', 'UBUNTU 22.04'),
]

pc = portal.Context()
pc.defineParameter("num_nodes", "Number of r7525 nodes",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("os_image", "OS image",
                   portal.ParameterType.IMAGE, imageList[0], imageList)
pc.defineParameter("data_size", "local storage size",
                   portal.ParameterType.STRING, "512GB")
params = pc.bindParameters()

request = pc.makeRequestRSpec()

reglan = request.LAN("regLAN")
reglan.best_effort = True
reglan.vlan_tagging = True
reglan.link_multiplexing = True
bflan = request.LAN("bfLAN")

for i in range(params.num_nodes):
    node = request.RawPC("node{}".format(i + 1))
    node.disk_image = params.os_image
    node.hardware_type = 'r7525'
    bs = node.Blockstore("bs{}".format(i + 1), "/data")
    bs.size = params.data_size
    # ConnectX-5 25Gbps
    iface = node.addInterface("eth1")
    iface.bandwidth = 25600
    iface.addAddress(rspec.IPv4Address(
        "192.168.1.{}".format(i + 1), "255.255.255.0"))
    reglan.addInterface(iface)
    # Initialize BlueField DPU.
    bfif = node.addInterface("bf")
    bfif.addAddress(rspec.IPv4Address(
        "11.11.11.{}".format(i + 1), "255.255.255.0"))
    bfif.bandwidth = 100000000
    bflan.addInterface(bfif)

pc.printRequestRSpec(request)
