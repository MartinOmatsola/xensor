#
# Installation code for ubuntu guests
# Inherits methods from DebianOS
# Post-installation differs slightly from DebianOS
#    ->/etc/apt/sources.list is different
#    ->disabling ttys is different for edgy
#
# Copyright 2007
# Martin Okorodudu <martin.omatsola@gmail.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.

import util, os
from Debian import DebianOS

class UbuntuOS(DebianOS):
        
    
    def post_install(self):
        #create /etc/fstab, /etc/hostname, /etc/network/interfaces, /etc/hosts
        #create xen config file, unmount disk image
        
        mnt_pt = "/mnt/%s" % self._name 
        
        print "Setting up guest OS %s\n" % self._name
        
        print "Copying kernel modules\n"
        self.copy_kernel_modules(mnt_pt)
        
        print "Disabling extra ttys\n" 
        self._disable_ttys(mnt_pt)     
             
        print "Setting up apt\n" 
        text = """# %s/stable
deb http://archive.ubuntu.com/ubuntu/ %s main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu %s-security main restricted universe multiverse

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
        
       
    def _disable_ttys(self, mnt_pt):
        util.run_command("rm -f %s/etc/event.d/tty[2-6]" % mnt_pt)
        lines = util.pipe_command("cat %s/etc/event.d/tty1" % mnt_pt)
        if self._release == "feisty":
            lines[-1] = 'exec /sbin/getty -L 9600 console vt100\n'
        else:
            lines[-1] = 'respawn /sbin/getty -L 9600 console vt100\n'
            
        fd = None
        try:
            fd = open("%s/etc/event.d/tty1" % mnt_pt, "w")
            fd.writelines(lines)
        finally:
            if fd is not None:
                fd.close()
        