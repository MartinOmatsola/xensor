#
# Base class for all guest domains
#
# Copyright 2007
# Martin Okorodudu <martin.omatsola@gmail.com>
# 
#
# This software may be freely redistributed under the terms of the GNU
# general public license.

import os, os.path, util

class GuestOS:
    
    #stores default parameters
    defaults = {
                "name" : "domU",
                "mem" : 128,
                "size" : 4,
                "fs" : "ext3",
                "kernel" : "/boot/vmlinuz-2.6.20-1.2933.fc6xen",
                "location" : "http://ftp.egr.msu.edu/debian",
                "arch" : "i386",
                "release" : "etch"
                }
    
    
    def __init__(self, config=None):
        """@config is a dictionary containing user specified parameters
           @name is the hostname of the guest domain
           @mem is the size of RAM in megabytes
           @size is the size of the disk image in gigabytes
           @path is the path to the disk image
           @fs is the filesystem type ie ext3, ext2, reiserfs
           @swap is the path to the swap image
           @swapsize is the size of the swap image in megabytes
           @release is the release version of the OS
           @arch is the cpu architecture ie ia64, i386 etc
           @kernel is the xen kernel to use
           @location is the install location, nfs, http, or ftp"""
           
        #override defaults   
        if config is not None:
           self.defaults.update(config)
        
        if not self.defaults.has_key("path"):
            self.defaults["path"] = "/var/lib/xen/images/%s.img" % self.defaults["name"]
        if not self.defaults.has_key("swap"):    
            self.defaults["swap"] = "/var/lib/xen/images/%s-swp.img" % self.defaults["name"]
        if not self.defaults.has_key("swapsize"):  
            self.defaults["swapsize"] = 2 * self.defaults["mem"]
           
        self._name = self.defaults["name"]
        self._mem = self.defaults["mem"]
        self._size = self.defaults["size"]
        self._path = self.defaults["path"]
        self._fs = self.defaults["fs"]
        self._swap = self.defaults["swap"]
        self._swapsize = self.defaults["swapsize"]
        self._kernel = self.defaults["kernel"]
        self._location = self.defaults["location"]
        self._arch = self.defaults["arch"]
        self._release = self.defaults["release"]
        
    
    def get_name(self):
        return self._name
    name = property(fget=get_name)
    
    
    def get_mem(self):
        return self._mem
    mem = property(fget=get_mem)
    
    
    def get_size(self):
        return self._size
    size = property(fget=get_size)
    
    
    def get_path(self):
        return self._path
    path = property(fget=get_path)
    
    
    def get_fs(self):
        return self._fs
    fs = property(fget=get_fs)
    
    
    def get_swap(self):
        return self._swap
    swap = property(fget=get_swap)
    
    
    def get_swapsize(self):
        return self._swapsize
    swapsize = property(fget=get_swapsize)
    
    
    def get_kernel(self):
        return self._kernel
    kernel = property(fget=get_kernel)
    
    
    def get_location(self):
        return self._location
    location = property(fget=get_location)
    
    
    def get_arch(self):
        return self._arch
    arch = property(fget=get_arch)
    
    
    def get_release(self):
        return self._release
    release = property(fget=get_release)
    
    
    def create_disks(self):
       """create root and swap images"""
       #check if image already exists, if it does use it
       print "Creating disk image %s\n" % self._path
       if not os.path.isfile(self._path):
           if not util.create_image(self._path, self._size):
                
               print"Formatting %s as %s" % (self._path, self._fs)
               if util.format_fs(self._path, self._fs) :
                   print "%s not supported\nExiting" % self._fs
           else:    
               print "Could not create disk image\nExiting"
               return 1
       else:
           print "%s exists, using existing image\n" % self._path
        
       #check if swap image exists, if it does use it
       print "Creating swap image %s\n" % self._swap
       if not os.path.isfile(self._swap):
           if not util.create_image(self._swap, self._swapsize, "M"):
               util.format_fs(self._swap, "swap")
           else:    
               print "Could not create swap image\nExiting"
               return 1
       else:
           print "%s exists, using existing image\n" % self._swap
            
    
    def create_fstab(self, mnt_pt):
        
        text = """/dev/hda1\t/\text3\tdefaults,errors=remount-ro\t0\t1
/dev/hda2\tnone\tswap\tsw\t0\t0
proc\t/proc\tproc\tdefaults\t0\t0

"""
        util.write_to_file("%s/etc/fstab" % mnt_pt, "w", text)
    
    
    def create_initrd(self):
        kernel_version = os.path.basename(self._kernel)[8:]
        util.run_command("mkinitrd -v -f --with=%s --with=xenblk \
                    /boot/initrd-%s.img %s" % (self._fs, self._name, kernel_version))
    
    
    def network_setup(self, mnt_pt):
        
        util.write_to_file("%s/etc/hostname" % mnt_pt, "w", self._name + "\n")
        
        util.write_to_file("%s/etc/hosts" % mnt_pt, "w", "127.0.0.1 localhost %s\n" % self._name)
        
        text = """auto lo
iface lo inet loopback
        
auto eth0
iface eth0 inet dhcp

"""
        util.write_to_file("%s/etc/network/interfaces" % mnt_pt, "w", text)
    
    
    def create_xen_config(self):
        
        text = """kernel = "%s"
ramdisk = "/boot/initrd-%s.img"
memory = %s
name = "%s"
disk = ['file:%s,hda1,w','file:%s,hda2,w']
vif = ['bridge=xenbr0']
root = "/dev/hda1 ro"

""" % (self._kernel, self._name, self._mem, 
                   self._name, self._path, self._swap)
        
        util.write_to_file("/etc/xen/%s" % self._name, "w", text)
             
        
    def copy_kernel_modules(self, mnt_pt):
        #disable hw clock
        #os.chmod("%s/etc/init.d/hwclock.sh" % mnt_pt, 0644)
        
        #copy kernek modules
        kernel_version = os.path.basename(self._kernel)[8:]
        util.run_command("cp -r /lib/modules/%s \
                    %s/lib/modules/%s" % (kernel_version, mnt_pt, kernel_version)) 
        