#
# Installation code for debian guests
#
# Copyright 2007
# Martin Okorodudu <martin.omatsola@gmail.com>
# 
#
# This software may be freely redistributed under the terms of the GNU
# general public license.

import os, os.path, util
from Guest import GuestOS

class DebianOS(GuestOS):
    
    
    def pre_install(self):
        """Create disk image, swap image"""
        
        self.create_disks()    
        return 0
    
    
    def install(self):
        """mount disk image and download base system"""
        
        #mount disk image
        mnt_pt = "/mnt/%s" % self._name
        os.mkdir(mnt_pt)
        util.run_command("mount -o loop %s %s" % (self._path, mnt_pt))
        
        #download base system
        print "Downloading %s base system\n" % self._release
        return util.run_command("debootstrap --arch %s %s %s %s" % 
                  (self._arch, self._release, mnt_pt, self._location))
        
    
    def post_install(self):
        #create /etc/fstab, /etc/hostname, /etc/network/interfaces, /etc/hosts
        #create xen config file, unmount disk image
        
        mnt_pt = "/mnt/%s" % self._name 
        
        print "Setting up guest OS %s\n" % self._name
        
         #disable tls
        os.rename("%s/lib/tls" % mnt_pt, "%s/lib/tls.disabled" % mnt_pt)
        
        print "Copying kernel modules\n"
        self.copy_kernel_modules(mnt_pt)
             
        print "Disabling extra ttys\n"
        self._disable_ttys(mnt_pt)
        
        print "Setting up apt\n" 
        text = """# %s/stable
deb http://ftp.debian.org/debian/ %s main contrib non-free
deb http://security.debian.org %s/updates main contrib non-free

""" % (self._release, self._release, self._release)
           
        self._apt_setup(text, mnt_pt)
          
        print "installing libc6-xen, udev, ssh\n"   
        self.install_pkgs(["libc6-xen", "openssh-server", "udev"], mnt_pt)
        
        #create /etc/fstab
        print "Setting up filesystem table\n"
        self.create_fstab(mnt_pt)
            
        print "Setting up networking\n"
        self.network_setup(mnt_pt)
            
        #hack to prevent nash-hotplug from hogging cpu
        self.kill_nash_hotplug(mnt_pt)
            
        print "Creating initrd for %s\n" % self._name
        self.create_initrd()
        
        print "Generating xen configuration file /etc/xen/%s\n" % self._name
        self.create_xen_config()
                
        #unmount filesystem
        util.run_command("umount %s" % mnt_pt)
        os.rmdir(mnt_pt)
        
        print "Installation of guest domain %s complete!!!" % self._name
        return 0
        
        
    def install_package(self, path, pkg):
        util.run_command("DEBIAN_FRONTEND=noninteractive chroot %s \
                    /usr/bin/apt-get --yes --force-yes install %s" % (path, pkg))
        
    
    def kill_nash_hotplug(self, mnt_pt):
        
        filename = "%s/etc/rc2.d/S05kill-nash-hotplug" % mnt_pt
        util.write_to_file(filename, "w", "pkill nash-hotplug\n")
        os.chmod("%s/etc/rc2.d/S05kill-nash-hotplug" % mnt_pt, 0777)
    
    
    def _apt_setup(self, text, mnt_pt):
        
        filename = "%s/etc/apt/sources.list" % mnt_pt
        util.write_to_file(filename, "w", text)
        util.run_command("chroot %s /usr/bin/apt-get update" % mnt_pt)    
        
   
    def install_pkgs(self, pkg_lst, mnt_pt):     
        
        for pkg in pkg_lst:
            self.install_package(mnt_pt, pkg)
            
        #clean apt package cache
        util.run_command("chroot %s /usr/bin/apt-get clean" % mnt_pt)
            
                
    def _disable_ttys(self, mnt_pt):
        
        #disable gettys
        util.run_command("sed -i -e 's/^\([1-6].*:respawn*\)/#\1/' -e 's/^T/#\t/' %s/etc/inittab" % mnt_pt)
        
        text = "S0:12345:respawn:/sbin/getty -L console 9600 vt100\n"
        util.write_to_file("%s/etc/inittab" % mnt_pt, "a", text)
        
        