import signal

global interruption
interruption = False

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    global interruption
    interruption = True


signal.signal(signal.SIGTERM, handler)

while interruption == False:
    pass

print 'AHA'

