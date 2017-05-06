#!/usr/bin/env python

# Main sysinfor application
# todo:
#  Config:
#   Define base directory
#   Define modules
#   Define module configs
#  Options:
#    Cron
#      Walk through module cron needs
#    Refresh all data
#

# Options
# -c/--config = short or full path to config file
# -h/--help = help
# -m/--module(s) = what modules to work on (can be comma seperated)
# -l/--list = List available modules
# === Next ones can be limited to specific modules with -m ===
# --cron = run through cron
# -r/--refresh = refresh data

import ConfigParser
import argparse
import os
import sys

# Some default vars
standardConfigFile = "sysinfor.config"

# Error handling
# Code: What it means
# 1: Unable to read config file passed in using -c/--config
# 2: Informaton passed using -c/--config is not a file or does not exists
#
def handleError(error, code):
    # I don't do anything currently, might need to fix that.
    print "Error Code: " + code
    sys.exit(error)


def getOpts():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--config",
                        action = "store",
                        metavar = "Config",
                        dest = "config",
                        help = "Configuration file to use")
    parser.add_argument('-m', "--modules",
                        action = "store",
                        metavar = "module1[,module2,module3]",
                        dest = "modules",
                        nargs = "?",
                        help = "List of modules to work on")
    parser.add_argument('-l', "--list",
                        action = "store_true",
                        default = False,
                        dest = "list",
                        help = "List available modules")
    parser.add_argument('--cron',
                        action = "store_true",
                        default = False,
                        dest = "cron",
                        help = "Run cron jobs, limit with -m")
    parser.add_argument('-r', "--refresh",
                        action = "store_true",
                        default = False,
                        dest = "refresh",
                        help = "Refresh data, limit with -m")
    return parser.parse_args()


if __name__ == "__main__":
    args = getOpts()
    defConfigFileLocation = os.path.dirname(os.path.realpath(__file__))
    defConfigFile = defConfigFileLocation + "/" + standardConfigFile
    configFile = defConfigFile
    if args.config is not None:
        tmpConfig = args.config
        if os.path.isfile(tmpConfig):
            if os.access(tmpConfig, os.R_OK):
                configFile = tmpConfig
            else:
                handleError("Unable to read given config file: " + tmpConfig, "1")
        else:
            handleError("Config file does not exist or is not a file", "2")
