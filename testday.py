#!/usr/bin/python

import argparse
import datetime
import os
import sys


scriptdir = os.path.dirname(__file__)
quick_mail_template = file(os.path.join(scriptdir,
    "early-mail-template.txt")).read()
mail_templates = file(os.path.join(scriptdir, "mail-templates.txt")).read()


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
