#Phone specific constants should go here.


PRODUCT_INIT_EXTRA_LONG_ADB_HANG_RECOVERY_TIMEOUT=0

INTERNAL_ADB_HANG_RECOVERY=False
INTERNAL_ADB_HANG_RECOVERY_TIMEOUT=0
INTERNAL_ADB_HANG_RECOVERY_DELAY=0

INTERNAL_RETRY_ON_CONNECTION_ERROR=False
INTERNAL_RETRY_ON_CONNECTION_ERROR_RETRIES=0
INTERNAL_RETRY_ON_CONNECTION_ERROR_DELAY=0

"""
These panic and log folders and individual files are copied from the phone
after each test method has completed.
"""

LOCATIONS_PULLED_AFTER_EACH_TEST=["/data/dontpanic",

                            "/data/tombstones",

                            #"/sdcard/app_dump",

                            # I found files /data/logger/aplogd.db and
                            # bplogd.clog not appearing in
                            # AndroidLogsLocations, so I'm pulling all of
                            # /data/logger.
                            "/data/logger",
                            #"/sdcard/AOL_*",
                            "/sdcard/logger",
                            "/sdcard-ext/logger",
                            "/data/panic",
                            "/sdcard/app_dump",
                            "/data/panic_data",

                            # /data/kernelpanics does not appear in the
                            # AndroidLogsLocations page, but I've seen
                            # it on the phone.
                            "/data/kernelpanics",
                            "/data/kernel_panics",

                            "/data/panicreports",
                            "/data/anr",
                            "/data/panic_report.txt"]


"""
These individual files are copied from the phone after apython has recovered a
connection to the phone.
"""
FILES_PULLED_ON_CONNECTION_RECOVERY=["/proc/bootinfo", "/proc/uptime"]

LOG_ON_RUNTESTS_CONNECT=[( ' logcat -v threadtime', 'logcat_main.txt' ), ( ' cat /proc/kmsg', 'kmsg.txt' ),]

FTP_URL = '144.190.68.124'

FTP_USERNAME = '3gsystest2'

FTP_PASSWORD = 'circle_M'

FTP_DOWNLOAD_FILE = 'humpty_10MB.txt'

FTP_UPLOAD_FILE = 'binary_file.bin'
