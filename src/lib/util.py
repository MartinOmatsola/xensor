# Contains general functions needed during installation
#
# Copyright 2007
# Martin Okorodudu <martin.omatsola@gmail.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.


import os

def create_image(path, size, unit="G"):
    """Create a blank disk image"""
    
    factor = 1024L * 1024L * 1024L
    
    if unit == "M": factor = 1024L * 1024L
    elif unit == "K": factor = 1024L
    elif unit  == "B": factor == 1
    
    fd = None
    try: 
        size_bytes = long(size * factor)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT)
        os.lseek(fd, size_bytes, 0)
        os.write(fd, '\x00')
    finally:
        if fd is not None:
            os.close(fd)            
     
    #check if file exists
    if not os.path.isfile(path):
        return 1
     
    return 0
        

def format_fs(path, fs="ext3"):
    
    cmd = ""
    if fs.startswith("ext"):
        cmd = "mkfs." + fs + " -F"
    elif fs == "reiserfs":
        cmd = "mkfs." + fs + " -q"   
    elif fs == "swap":
        cmd = "mkswap"
    else:
        return 1  
        
    run_command("%s %s" % (cmd , path))
    
    return 0 

    
def run_command(cmd):
    return os.system(cmd)


def pipe_command(cmd):
    pipe = os.popen(cmd)
    res = [line for line in pipe]    
    pipe.close()
    return res


def write_to_file(filename, mode, text):
    fd = None
    try:
        fd = open(filename, mode)
        fd.write(text)
    finally:
        if fd is not None:
            fd.close()
            
