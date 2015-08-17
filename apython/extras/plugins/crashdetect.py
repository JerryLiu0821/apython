"""
To install and enable, copy this file to $TOP/plugins/ where $TOP is the
directory where runtests.py is located, then add this line to your settings
file:

EXPERIMENTAL_CRASH_DETECT_SUPPORT=True

This plugin enables the use of the AppCrashDetector by runtests.py to
detect ANRs and force closes. runtests.py will start ACD before executing
a test and stop ACD after each test completes. If ANRs or force closes are
detected, additional logs (FCs.*.txt, ANRs.*.txt) will appear in the log
directory for the test. This plugin assumes the AppCrashDetector code has
already been pushed to the device.

You may obtain a copy of AppCrashDetector from:
http://mapps-test.sourceforge.mot-mobility.com/temp/AppCrashDetector.zip

AppCrashDetector works on Eclair and later versions of Android.
"""

import android

# XXX: Report # ANRs, FCs in summary report
@android.register_connect_hook
def __crashdetect_connect_hook(a, connecting):
    if not hasattr(a.settings, 'EXPERIMENTAL_CRASH_DETECT_SUPPORT'): return

    TAG = 'crashdetect'

    if connecting:
        android.log.info(TAG, 'Connecting')
        a.internal.crashdetect = a.internal.transport.popen('acd.sh')
        time.sleep(1)    # allow it time to start up
        output = a.device.sh(    'AppCrashDetector.sh config -1 1;'
                                'AppCrashDetector.sh logConsole 1')
        if 'false' in output or 'not found' in output or 'Exception' in output:
            android.log.error(TAG, 'Startup error')
            a.device.sh('AppCrashDetector.sh shutdown')
            a.internal.crashdetect.communicate()
            del a.internal.crashdetect
        return

    # disconnecting
    if 'crashdetect' not in dir(a.internal):
        return

    android.log.info(TAG, 'Disconnecting')
    a.device.sh('AppCrashDetector.sh shutdown')
    output=a.internal.crashdetect.communicate()[0]
    IDLE,IN_ANR,IN_FC=range(3)
    state, ANRs, FCs = IDLE, [], []
    for o in output.splitlines():
        if state is not IDLE and len(o) is 0:
            state = IDLE
        elif state is IN_ANR:
            ANRs[-1] += o + '\n'
        elif state is IN_FC:
            FCs[-1] += o + '\n'
        else:
            assert state is IDLE
            if o.startswith('// CRASH'):
                state = IN_FC
                FCs.append(o + '\n')
            elif o.startswith('// NOT RESPONDING'):
                state = IN_ANR
                ANRs.append(o + '\n')
    if len(FCs) is not 0:
        android.log.warning(TAG, '%d force closes detected' % len(FCs))
        f=open(a.log.log_filename('FCs.txt'),'wb')
        for FC in FCs: f.write(FC + '\n')
        f.close()
    if len(ANRs) is not 0:
        android.log.warning(TAG, '%d ANRs detected' % len(ANRs))
        f=open(a.log.log_filename('ANRs.txt'),'wb')
        for ANR in ANRs: f.write(ANR + '\n')
        f.close()
    del a.internal.crashdetect
