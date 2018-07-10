# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'yaml'

unless Vagrant.has_plugin?("vagrant-vbguest")
  raise 'vagrant plugin vbguest is not installed! Run \"vagrant plugin install vagrant-vbguest\"'
end

unless Vagrant.has_plugin?("vagrant-hosts")
  raise 'vagrant plugin host is not installed! Run \"vagrant plugin install vagrant-hosts\"'
end

## Debug
#config.vm.provision "shell", inline: "echo \"share: #{mount['mountpoint']}\"

nodes_config = (JSON.parse(File.read("nodes.json")))['nodes']

Vagrant.configure(2) do |config|

  nodes_config.each do |node|
    node_name   = node[0] # name of node
    node_values = node[1] # content of node
    config.vbguest.auto_update = true

    config.vm.define node_name do |config|

      # configures all forwarding ports in JSON array
      ports = node_values['ports']
      ports.each do |port|
        config.vm.network :forwarded_port,
          host:  port[':host'],
          guest: port[':guest'],
          id:    port[':id']
      end
 
      config.vm.hostname = node_name
      config.vm.box = node_values[':box']
      config.vm.network :private_network, ip: node_values[':ip']
 
      config.vm.provider :virtualbox do |vb|
        vb.name = node_name 
        vb.memory = node_values[':memory']
      end

      #config.vm.provision :hosts do |provisioner|
      #  provisioner.add_host '172.20.16.14', ['puppet.register.it', 'puppetmaster.register.it','puppetmaster.local','puppet.vagrant']
      #  provisioner.add_host '10.20.1.20', ['popper.it.filer']
      #end
 
      config.vm.provision :shell, :path => node_values[':bootstrap']

      #config.vm.synced_folder ".", "/vagrant", disabled: false
      #config.vm.synced_folder ".", "/vagrant"

      #config.vm.provision :shell,  inline: "/bin/mount -a", run: 'always'

      mounts = node_values['mounts']

      if mounts.is_a?(Array)
          mounts.each do |mount|
              config.vm.synced_folder mount['share'] , mount['mountpoint']
          end
      end
    end
  end
end
