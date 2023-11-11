from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel,info
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI

class NetworkTopo(Topo):

   def __init__(self, link_loss, **opts):

       Topo.__init__(self, **opts)

       h1 = self.addHost(name='h1', ip='10.0.0.1')
       h2 = self.addHost(name='h2', ip='10.0.0.2')
       h3 = self.addHost(name='h3', ip='10.0.0.3')
       h4 = self.addHost(name='h4', ip='10.0.0.4')
       leftSwitch = self.addSwitch('s1')
       rightSwitch = self.addSwitch('s2')

       self.addLink(leftSwitch, rightSwitch, loss=int(link_loss))
       self.addLink(leftSwitch,
                    h1,
                    intfName2='h1-eth1',
                    params2={'ip': '10.0.0.1/24'})
       self.addLink(leftSwitch,
                    h2,
                    intfName2='h2-eth1',
                    params2={'ip': '10.0.0.2/24'})
       self.addLink(rightSwitch,
                    h3,
                    intfName2='h3-eth2',
                    params2={'ip': '10.0.0.3/24'})
       self.addLink(rightSwitch,
                    h4,
                    intfName2='h4-eth2',
                    params2={'ip': '10.0.0.4/24'})


def runExperiment(config, congestion_scheme, link_loss):

   topo = NetworkTopo(link_loss)
   net = Mininet(topo, link=TCLink)
   net.start()
  
   if config == 'b':
       # Run the client on H1 and the server on H4
       h1 = net.get('h1')
       h4 = net.get('h4')
       net['h4'].cmd(f'iperf -s -p 1234 &')
       net['h4'].cmd('timeout 15000 tcpdump -i h4-eth2 -w server_h4.pcap &')
       net['h1'].cmd('timeout 15000 tcpdump -i h1-eth1 -w client_h1.pcap &')
       net['h1'].cmd(f'iperf -c 10.0.0.4 -p 1234 -Z {congestion_scheme} &')

   elif config == 'c':
       # Run clients on H1, H2, H3 simultaneously and the server on H4
       h1 = net.get('h1')
       h2 = net.get('h2')
       h3 = net.get('h3')
       h4 = net.get('h4')
       net['h4'].cmd(f'iperf -s -p 1234 &')
       net['h4'].cmd(f'iperf -s -p 1235 &')
       net['h4'].cmd(f'iperf -s -p 1236 &')
       net['h4'].cmd('timeout 15000 tcpdump -i h4-eth2 -w server_h4.pcap &')
       net['h3'].cmd('timeout 15000 tcpdump -i h3-eth2 -w client_h3.pcap &')
       net['h2'].cmd('timeout 15000 tcpdump -i h2-eth1 -w client_h2.pcap &')
       net['h1'].cmd('timeout 15000 tcpdump -i h1-eth1 -w client_h1.pcap &')
       net['h1'].cmd(f'iperf -c 10.0.0.4 -p 1234 -Z {congestion_scheme} &')
       net['h2'].cmd(f'iperf -c 10.0.0.4 -p 1235 -Z {congestion_scheme} &')
       net['h3'].cmd(f'iperf -c 10.0.0.4 -p 1236 -Z {congestion_scheme} &')

   else:
       print("Invalid configuration. Use 'b' or 'c'.")
  
   CLI(net)

   net.stop()

if __name__ == '__main__':
   setLogLevel('info')
   config = input("Enter configuration (b/c): ")
   congestion_scheme = input("Enter congestion control scheme: ")
   link_loss = input("Enter link loss percentage: ")
   runExperiment(config, congestion_scheme, link_loss)