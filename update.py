#!/usr/bin/python

import sys
import datetime
import string
import xdaapi
import re

def main(argc, argv):
    i = 1
    user=""
    password=""
    opdata=""
    version=""
    device=""
    postid=""
    title=""
    showdate=""

    while i < argc:
        if argv[i] == "-u":
            i+=1
            user = argv[i]
        elif argv[i] == "-p":
            i+=1
            password = argv[i]
        elif argv[i] == "-v":
            i+=1
            version = argv[i]
        elif argv[i] == "-d":
            i+=1
            device = argv[i]
        elif argv[i] == "-i":
            i+=1
            postid = argv[i]
        elif argv[i] == "-t":
            i+=1
            showdate= argv[i]
        else:
            print "Invalid argument " + argv[i]
            return 1

        i += 1

    if not user or not password:
        print "User name and password are required, use -u and -p arguments!"
        return 1

    if not version:
        print "Version is required, use -v!"
        return 1

    if not showdate:
        showdate = datetime.datetime.now().strftime("%Y-%m-%d").upper()
    title = "[RECOVERY][%s] TWRP %s touch recovery [%s]" % (device, version, showdate)
    if not device:
        title = "[RECOVERY] TWRP %s touch recovery [%s]" % (version, showdate)
    api=xdaapi.XdaApi()
    api.login(user, password)

    with open ("op.txt", "r") as opfile:
        opdata=opfile.read()

    list = open("list.txt", "r")
    for line in list:
        currdevice, postid = line.split("=", 1)
        if not device or device == currdevice:
            print "Working on " + currdevice
            title = "[RECOVERY][%s] TWRP %s touch recovery [%s]" % (currdevice, version, showdate)
            api.save_raw_post(postid, title, opdata)

    api.logout_user()
    return 0

if __name__ == "__main__":
   exit(main(len(sys.argv), sys.argv))

