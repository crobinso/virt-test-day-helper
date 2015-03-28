#!/usr/bin/python

import argparse
import datetime
import os
import sys


quick_mail_template = """
============================================
=== Fedora virt quick announce, and blog ===
============================================

SUB: Fedora ZZZFEDZZZ Virt Test Day scheduled for ZZZDATEZZZ
TO: virt@lists.fedoraproject.org

Hey all,

Just a quick note that the Fedora ZZZFEDZZZ Virt Test Day is scheduled for ZZZDATEZZZ. The inprogress landing page is at:

ZZZLINKZZZ

So if you're interested in helping test new virt features, or you want to make sure that the stuff you care about isn't broken, please mark your calendars.

Thanks,
Cole
"""

mail_templates = """
=====================
=== public emails ===
=====================

SUB: Fedora ZZZFEDZZZ Virt Test Day is ZZZDATEZZZ!
TO: test-announce@lists.fedoraproject.org

TO: virt@lists.fedoraproject.org

FWD: xen@lists.fedoraproject.org  , brief bit that all testing helps and we will have libvirt people on hand

FWD: qe-dept-list@redhat.com
FWD: Blog this as well, with better formatting

Hey all,

The Fedora ZZZFEDZZZ Virt Test Day is this coming ZZZDATEZZZ. Check out the test day landing page:

ZZZLINKZZZ

If you're interested in trying out some new virt functionality, there's step by step instructions for:

* ZZZFEATURESZZZ

Even if you aren't interested in testing new features, we still need you! The test day is the perfect time to make sure your virt workflow is working fine on Fedora ZZZFEDZZZ, as there will be several developers on hand to answer any questions, help with debugging, provide patches, etc. No requirement to run through test cases on the wiki, just show up and let us know what works (or breaks).

And to be clear, while it is preferred that you have a physical machine running Fedora ZZZFEDZZZ, participating in the test day does NOT require it: you can test the latest virt bits on the latest Fedora release courtesy of the virt-preview repo. For more details, as well as easy instructions on updating to Fedora ZZZFEDZZZ, see:

ZZZLINKZZZ#What.27s_needed_to_test

If you can't make the date of the test day, adding test case results to the wiki anytime next week is fine as well. Though if you do plan on showing up to the test day, add your name to the participant list on the wiki, and when the day arrives, pop into #fedora-test-day on freenode and give us a shout!

Thanks,
Cole



======================================
====== INTERNAL VIRT TEAM LIST =======
======================================

SUB: Fedora ZZZFEDZZZ Virt Test Day is ZZZDATEZZZ, how you can help
TO: eng-virt-staff-list
CC: virt-qe-list@redhat.com
CC: libvirt-qe@redhat.com

Hey all,

The Fedora ZZZFEDZZZ Virt Test Day is ZZZDATEZZZ. Here's the landing page:

ZZZLINKZZZ

It would really help if folks could spare 1-2 hours to bang on your specific area of virt expertise with the stock Fedora packages. Particularly if you already have setups for involved things like migration, device assignment, snapshots, etc. No obligation to fill out test results in the wiki, just make sure bugs are filed :)

There's documentation for all the different ways you can setup Fedora ZZZFEDZZZ for testing:

ZZZLINKZZZ#What.27s_needed_to_test

In order of increasing complexity:

- Install Fedora in a VM with nested virt.

- Run Fedora ZZZFEDZZZ packages on latest Fedora release with the virt-preview repo.

- Actually install Fedora ZZZFEDZZZ.

Helping out isn't limited to actually running test cases, just showing up in the IRC channel to answer questions is useful too. I think a strong developer presence is a good way to encourage test day participation from community folks.

If you plan on helping out, please do the following:

- Add your name and IRC nick to the 'Who's available' section on the landing page.

- On the test day, jump in #fedora-test-day on freenode and drop a greeting
  like 'hey all, just stopping in for the virt test day. I work on XYZ so if
  you've got any questions, ask away!'

And this message isn't aimed solely at qemu/kvm/libvirt devs, this (mostly) applies to you libvirt, virt-tools, spice, virtio win, QE and manager types too!

Thanks,
Cole
"""


###################
# Utility methods #
###################

def convert_date(date):
    fmt = "%Y-%m-%d"
    if type(date) is str:
        return datetime.datetime.strptime(date, fmt)
    else:
        return date.strftime(fmt)


def fail(msg):
    print >> sys.stderr, "ERROR: %s" % msg
    sys.exit(1)


def prompt():
    msg = "(press enter to continue)"
    sys.stdout.write(msg)
    return sys.stdin.readline()


######################
# Functional helpers #
######################

def generate_calendar_reminders(test_day_date):
    date = convert_date(test_day_date)

    ret = []
    def add_event(date, title, prefix=True):
        p = "TESTDAY: "
        if not prefix:
            p = ""
        ret.append("date:  %s\ntitle: %s%s" % (date, p, title))

    # Alpha event, we don't know date ahead of time
    add_event(
        "YYYY-MM-DD (you need to look it up)",
        "Alpha release candidates yet? If so, check steps.txt",
        prefix=False)

    # 2 weeks + 2 days before test day
    add_event(convert_date(date - datetime.timedelta(days=16)),
        "2 weeks before test day! Move project file to todo.txt, check it over")

    # 4 days before test day
    add_event(convert_date(date - datetime.timedelta(days=4)),
        "4 days before test day! Check steps.txt")

    # day before test day
    add_event(convert_date(date - datetime.timedelta(days=1)),
        "1 day before test day! Check steps.txt")

    # day of test day
    add_event(convert_date(date), "Day of test day! Check steps.txt")

    return "\n\n".join(ret)


def generate_mail_from_template(fedora_version, test_day_date, template):
    url = ("https://fedoraproject.org/wiki/Test_Day:%s_Virtualization" %
        test_day_date)

    ret = template
    ret = ret.replace("ZZZFEDZZZ", str(fedora_version))
    ret = ret.replace("ZZZLINKZZZ", url)
    ret = ret.replace("ZZZDATEZZZ",
        convert_date(test_day_date).strftime("%a %b %d"))
    return ret


###################
# main() handling #
###################

def parse_args():
    parser = argparse.ArgumentParser(
        description="Helper for organizing fedora test day todo items")

    parser.add_argument("fedora_version", type=int,
        help="Fedora version the test day is for, example: 22")
    parser.add_argument("test_day_date",
        help="Date of the test day, example: 2014-09-25")

    cgrp = parser.add_argument_group("Commands")
    cgrp.add_argument("--calendar", action="store_true",
        help="Generate calendar dates and titles")
    cgrp.add_argument("--emails", action="store_true",
        help="Generate email output for the specified date.")

    options = parser.parse_args()
    return options, parser


def main():
    options, parser = parse_args()
    fedora_version = options.fedora_version
    test_day_date = options.test_day_date

    if options.calendar:
        print "First, copy content for when test day is scheduled from "
        print "steps.txt to your todo list."
        prompt()
        os.system("clear")
        print "COPY ALL THIS TO YOUR todo.txt FILE!"
        print
        print "Calendar entries:"
        print generate_calendar_reminders(test_day_date)
        print
        print generate_mail_from_template(fedora_version, test_day_date,
            quick_mail_template)
    elif options.emails:
        ret = generate_mail_from_template(fedora_version, test_day_date,
            mail_templates)

        fname = os.path.expanduser("~/test-day-mails.txt")
        if os.path.exists(fname):
            fail("%s exists, move it please." % fname)

        print "Writing content to: %s" % fname
        open(fname, "w").write(ret)
        print "Done. Make sure to fill in the feature info, and test the URLs!"
    else:
        parser.error("A command must be specified.")


if __name__ == '__main__':
    sys.exit(main())
