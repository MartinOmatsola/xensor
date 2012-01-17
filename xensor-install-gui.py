#!/usr/bin/env python

#
# Installation via gui for debian guests
#
# Copyright 2007
# Martin Okorodudu <martin.omatsola@gmail.com>
# This software may be freely redistributed under the terms of the GNU
# general public license.

import sys, os
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

sys.path.append("src/lib")
import util

class Xensor:
    """This is an Hello World GTK application"""

    def __init__(self):

        #Set the Glade file
        self.gladefile = "src/xensor.glade"  
        self.wTree = gtk.glade.XML(self.gladefile)
        
        #set defaults
        self.wTree.get_widget("name").set_text("domU")
        self.wTree.get_widget("distro").set_active(0)
        self.wTree.get_widget("release").set_active(0)
        
        #get xen kernels
        klst = util.pipe_command("ls /boot | grep vmlinuz.*xen")
        if len(klst):
           for kernel in klst:
               self.wTree.get_widget("kernel").append_text("/boot/" + kernel[0:-1])
           self.wTree.get_widget("kernel").remove_text(0)
           self.wTree.get_widget("kernel").set_active(0)
            
        self.wTree.get_widget("path").set_text("/var/lib/xen/images/domU.img")
        self.wTree.get_widget("fs").set_active(0)
        self.wTree.get_widget("swap").set_text("/var/lib/xen/images/domU-swp.img")
        self.wTree.get_widget("size").set_text("4")
        self.wTree.get_widget("swapsize").set_text("256")
        self.wTree.get_widget("mem").set_text("128")
        self.wTree.get_widget("arch").set_active(0)
        self.wTree.get_widget("location").set_text("http://ftp.egr.msu.edu/debian")
        
        #assign our event handlers
        dic = {
               "on_install_clicked" : self.do_install,
               "on_distro_changed" : self.update_release, 
               "on_xensor_destroy" : gtk.main_quit
               }
        self.wTree.signal_autoconnect(dic)
        
        
    def do_install(self, widget):
        dic = {}
        dic["name"] = self.wTree.get_widget("name").get_text()
        
        model = self.wTree.get_widget("distro").get_model()
        active = self.wTree.get_widget("distro").get_active()
        dic["distro"] = model[active][0]
        
        model = self.wTree.get_widget("release").get_model()
        active = self.wTree.get_widget("release").get_active()
        dic["release"] = model[active][0]
        
        model = self.wTree.get_widget("kernel").get_model()
        active = self.wTree.get_widget("kernel").get_active()
        dic["kernel"] = model[active][0]
        
        dic["path"] = self.wTree.get_widget("path").get_text()
        
        model = self.wTree.get_widget("fs").get_model()
        active = self.wTree.get_widget("fs").get_active()
        dic["fs"] = model[active][0]
        
        dic["swap"] = self.wTree.get_widget("swap").get_text()
        
        if len(self.wTree.get_widget("size").get_text()) > 0:
            dic["size"] = int(self.wTree.get_widget("size").get_text())
        
        if len(self.wTree.get_widget("swapsize").get_text()) > 0:
            dic["swapsize"] = int(self.wTree.get_widget("swapsize").get_text())
        
        if len(self.wTree.get_widget("mem").get_text()) > 0:
            dic["mem"] = int(self.wTree.get_widget("mem").get_text())
        
        dic["location"] = self.wTree.get_widget("location").get_text()
        #print dic
        
        #remove empty entries
        for k,v in dic.items():
            if v == "": del(dic[k])
        
        os_class = "%sOS" % dic["distro"]
        exec("from %s import %s" % (dic["distro"], os_class))
        
        del(dic["distro"])
        
        exec("guest = %s(dic)" % os_class)
        
        if guest.pre_install() or guest.install() or guest.post_install():
            print "An error occured during execution\nExiting"
            sys.exit(1)

    
    def update_release(self, widget):
        model = self.wTree.get_widget("distro").get_model()
        active = self.wTree.get_widget("distro").get_active()
        distro = model[active][0]
        
        model = self.wTree.get_widget("release").get_model()
        self.wTree.get_widget("release").set_model(None)
        model.clear()
        if distro == "Ubuntu":
            for release in ["dapper", "edgy", "feisty", "hoary"]:
                model.append([release])
        elif distro == "Debian":
            for release in ["etch", "sarge", "sid"]:
                model.append([release])
        
        self.wTree.get_widget("release").set_model(model)
        self.wTree.get_widget("release").set_active(0)
        

if __name__ == "__main__":
    if os.geteuid() != 0:
        print "You must be root to run this program"
        sys.exit(1)
    
    gui = Xensor()
    gtk.main()
