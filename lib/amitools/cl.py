import argparse
common_argparser = argparse.ArgumentParser(
    add_help=False,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
common_argparser.add_argument('-r', '--region', default=None,
                        help='''Specify REGION as the web service region to use.
Overrides the value specified by AWS_DEFAULT_REGION.
''')

def sigint_exit(signum, frame):
    import sys
    sys.stderr.write('\n')
    sys.exit(1)

def clsetup():
    import signal
    signal.signal(signal.SIGINT, sigint_exit)

