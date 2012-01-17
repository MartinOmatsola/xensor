#!/usr/bin/env python

#
# Installation script for debian guests
#
# Copyright 2007
# Martin Okorodudu <martin.omatsola@gmail.com>
# This software may be freely redistributed under the terms of the GNU
# general public license.

from optparse import OptionParser
import sys, os
sys.path.append("src/lib")

#check root users
if os.geteuid() != 0:
    print "You must be root to run this script"
    sys.exit(1)

#setup command line options
parser = OptionParser()

parser.add_option("--name", help="the name of your domU",
                   metavar="NAME", dest="name", type="string")

parser.add_option("--distro", help="the linux distro e.g. debian, ubuntu, solaris",
                   metavar="RELEASE", dest="distro", type="string")

parser.add_option("--release", help="the release e.g. etch, sarge, dapper",
                   metavar="RELEASE", dest="release", type="string")

parser.add_option("--memory", help="the RAM in MB",
                   metavar="RAM", dest="mem", type="int")

parser.add_option("--size", help="the disk image size in GB",
                   metavar="SIZE", dest="size", type="int")

parser.add_option("--filesystem", help="the fs of the disk image eg ext2, ext3",
                   metavar="FS", dest="fs", type="string")

parser.add_option("--kernel", help="absolute path to xen kernel to use for domU",
                   metavar="KERNEL", dest="kernel", type="string")

parser.add_option("--location", help="the install location",
                   metavar="LOC", dest="location", type="string")

parser.add_option("--image", help="absolute path to the disk image to use for domU",
                   metavar="IMAGE", dest="path", type="string")

parser.add_option("--swap", help="absolute path to the swap image to use for domU",
                   metavar="SWAP", dest="swap", type="string")

parser.add_option("--swapsize", help="the swap image size in MB",
                   metavar="SWAPSIZE", dest="swapsize", type="int")

(options, args) = parser.parse_args()


#string representation of options looks like a dictionary
#so we use it to create dictionary that is passed
#to DebianOS constructor
x = str(options) 
exec("dic = %s" % x)
for opt,val in dic.items():
    if val is None: del(dic[opt])

#determine OS type
os_type = "debian"
if dic.has_key("distro"):
   os_type = dic["distro"] 
   del(dic["distro"])
   
os_type = os_type.capitalize()
os_class = "%sOS" % os_type

#import appropriate module
exec("from %s import %s" % (os_type, os_class))


guest = None
if len(dic) : 
    exec("guest = %s(dic)" % os_class)
else:
    exec("guest = %s()" % os_class)
    
if guest.pre_install() or guest.install() or guest.post_install():
    print "An error occured during execution\nExiting"
    sys.exit(1)
