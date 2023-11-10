from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopology(Topo):
    def build(self, **_opts):

        # Creating 3 routers ra, rb, and rc in three different subnets
        ra = self.addHost('ra', cls=LinuxRouter, ip='10.0.0.1/24')
        rb = self.addHost('rb', cls=LinuxRouter, ip='10.1.0.1/24')
        rc = self.addHost('rc', cls=LinuxRouter, ip='10.2.0.1/24')

        # Creating 6 hosts h1, h2, h3, h4, h5, and h6
        h1 = self.addHost(name='h1', ip='10.0.0.2/24', defaultRoute='via 10.0.0.1')
        h2 = self.addHost(name='h2', ip='10.0.0.3/24', defaultRoute='via 10.0.0.1')
        h3 = self.addHost(name='h3', ip='10.1.0.2/24', defaultRoute='via 10.1.0.1')
        h4 = self.addHost(name='h4', ip='10.1.0.3/24', defaultRoute='via 10.1.0.1')
        h5 = self.addHost(name='h5', ip='10.2.0.2/24', defaultRoute='via 10.2.0.1')
        h6 = self.addHost(name='h6', ip='10.2.0.3/24', defaultRoute='via 10.2.0.1')

        # Creating 3 switches s1, s2, and s3 for the three routers respectively
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Adding the router-switch links within the same subnet:

        # The router-switch link s1-ra
        self.addLink(s1, ra, intfName2='ra-eth1', params2={'ip': '10.0.0.1/24'})

        # The router-switch link s2-rb
        self.addLink(s2, rb, intfName2='rb-eth1', params2={'ip': '10.1.0.1/24'})

        # The router-switch link s3-rc
        self.addLink(s3, rc, intfName2='rc-eth1', params2={'ip': '10.2.0.1/24'})

        # Adding the links for the inter-router connections:

        # Adding link b/w ra and rb
        self.addLink(ra, rb, intfName1='ra-eth2', intfName2='rb-eth2', params1={'ip': '10.100.0.1/24'}, params2={'ip': '10.100.0.2/24'})
        # Adding link b/w rb and rc
        self.addLink(rb, rc, intfName1='rb-eth3', intfName2='rc-eth2', params1={'ip': '10.200.0.1/24'}, params2={'ip': '10.200.0.2/24'})
        # Adding link b/w rc and ra
        self.addLink(rc, ra, intfName1='rc-eth3', intfName2='ra-eth3', params1={'ip': '10.250.0.1/24'}, params2={'ip': '10.250.0.2/24'})

        # Finally, linking the switches to the hosts:

        # Adding hosts h1, h2 to switch s1
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        # Adding hosts h3, h4 to switch s2
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        # Adding hosts h5, h6 to switch s3
        self.addLink(h5, s3)
        self.addLink(h6, s3)

def run():
    topo = NetworkTopology()
    net = Mininet(topo=topo)

    # Configuring the routing for the networks which are not directly connected:

    # Adding route for ra-rb
    info(net['ra'].cmd("ip route add 10.1.0.0/24 via 10.100.0.2 dev ra-eth2"))
    # Adding route for ra-rc
    info(net['ra'].cmd("ip route add 10.2.0.0/24 via 10.250.0.1 dev ra-eth3"))
    # Adding route for rb-ra
    info(net['rb'].cmd("ip route add 10.0.0.0/24 via 10.100.0.1 dev rb-eth2"))
    # Adding route for rb-rc
    info(net['rb'].cmd("ip route add 10.2.0.0/24 via 10.200.0.2 dev rb-eth3"))
    # Adding route for rc-ra
    info(net['rc'].cmd("ip route add 10.0.0.0/24 via 10.250.0.2 dev rc-eth3"))
    # Adding route for rc-rb
    info(net['rc'].cmd("ip route add 10.1.0.0/24 via 10.200.0.1 dev rc-eth2"))

    net.start()

    # Printing the Routing Tables of the three routers
    info('*** Routing Tables on Routers:\n')
    for router in ['ra', 'rb', 'rc']:
        info(net[router].cmd('route'))

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()