#!/bin/sh
adb root
sleep 2
adb remount
echo "set language to english.."
adb shell setprop persist.sys.language en
echo "rebooting...."
adb reboot


