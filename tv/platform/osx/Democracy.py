import os
import sys
import Foundation

# =============================================================================

def activatePsyco():
    # Detect cpu type
    import subprocess
    p = subprocess.Popen(["uname", "-p"], stdout=subprocess.PIPE) 
    cpu = p.stdout.read().strip()
    p.stdout.close()

    # Activate only if we are on an Intel Mac.
    if cpu == 'i386':
        try:
            print "DTV: Intel CPU detected, using psyco charge profiler."
            import psyco
            psyco.profile()
        except:
            print "DTV: Error while trying to launch psyco charge profiler."

# =============================================================================

def launchDemocracy():
    # We can now import our stuff
    import platformutils
    platformutils.initializeLocale()
    import gtcache
    gtcache.init()
    import app
    import prefs
    import config

    # Tee output off to a log file
    class AutoflushingTeeStream:
        def __init__(self, streams):
            self.streams = streams
        def write(self, *args):
            for s in self.streams:
                s.write(*args)
                s.flush()

    logFile = config.get(prefs.LOG_PATHNAME)
    if logFile:
        h = open(logFile, "wt")
        sys.stdout = AutoflushingTeeStream([h, sys.stdout])
        sys.stderr = AutoflushingTeeStream([h, sys.stderr])

    # Kick off the application
    app.main()

# =============================================================================

def getModulePath(name):
    import imp
    mfile, mpath, mdesc = imp.find_module(name)
    if mfile is not None:
        mfile.close()
    return mpath

def launchDownloaderDaemon():
    # Increase the maximum file descriptor count (to the max)
    import resource
    print "DTV: Increasing file descriptor count limit in Downloader."
    resource.setrlimit(resource.RLIMIT_NOFILE, (-1,-1))

    # Insert the downloader private module path
    daemonPath = getModulePath('dl_daemon')
    daemonPrivatePath = os.path.join(daemonPath, 'private')
    sys.path[0:0] = [daemonPath, daemonPrivatePath]
    
    # And launch
    import Democracy_Downloader
    Democracy_Downloader.launch()

# =============================================================================

# If the bundle is an alias bundle, we need to tweak the search path
bundle = Foundation.NSBundle.mainBundle()
bundleInfo = bundle.infoDictionary()
if bundleInfo['PyOptions']['alias']:
    root = os.path.dirname(bundle.bundlePath())
    root = os.path.join(root, '..', '..')
    root = os.path.normpath(root)
    sys.path[0:0] = ['%s/portable' % root]

# Activate psyco, if we are running on an Intel Mac
#
# We currently dont do it because psyco does not work correctly on Intel Macs 
# yet, as explained here: 
# http://mail.python.org/pipermail/pythonmac-sig/2006-June/017533.html

#activatePsyco()


# Launch player or downloader, depending on command line parameter
if len(sys.argv) > 1 and sys.argv[1] == "download_daemon":
    launchDownloaderDaemon()
else:
    launchDemocracy()

