def get_args(argv=None):
    from amitools import common_argparser
    import argparse
    import re
    parser = argparse.ArgumentParser(
        description='Tag an existing image with the amitools tags',
        epilog='''CREATION DATE AND TIME
There are two tags encoding when the image was made: create_date and
create_timestamp. They are meant to indicate the same moment in time,
just in differently convenient formats.

They are controlled by this script via the --create-date and
--create-timestamp options. To help prevent subtle bugs in which they
differ, you must supply exactly one of these options, but *not
both*. Whichever you supply will be used to calculate the other.
''',
        parents = [common_argparser],
        )
    parser.add_argument('--source-image', required=True,
                        help='Image ID of source AMI (tag: source_image)')
    parser.add_argument('--source-instance', required=True,
                        help='ID of source instance (tag: source_instance)')
    parser.add_argument('--source-region', required=True,
                        help='Region for the source AMI (tag: source_region)')
    parser.add_argument('--create-date', default=None,
                        help='Creation date, in UTC/GMT, like "20110909T233600Z" (tag: create_date)')
    parser.add_argument('--create-timestamp', default=None, type=int,
                        help='Creation timestamp, in seconds since the epoch (tag: create_timestamp)')
    parser.add_argument('image_id',
                        help='ID of AMI to set tags on')
    args = parser.parse_args(argv)

    # custom arg validation
    if args.create_timestamp is None and args.create_date is None:
        parser.error('You must supply exactly one of the --create_date or --create_timestamp options')
    if (args.create_timestamp is not None) and (args.create_date is not None):
        parser.error('You must supply just one of the --create_date or --create_timestamp options, but not both')
    if not re.match(r'ami-', args.image_id):
        parser.error('image_id must start with "ami-"')
    if not re.match(r'ami-', args.source_image):
        parser.error('source_image must start with "ami-"')
    if not re.match(r'i-', args.source_instance):
        parser.error('source_instance must start with "i-"')
    if (args.create_date is not None) and not re.match(r'\d{8}T\d{6}Z$', args.create_date):
        parser.error('If supplied, create_date must be a UTC date-time formated like "YYYYMMDDTHHMMSSZ"')
        
    return args

def main(args):
    import datetime
    from amitools.dt import dateparse
    from amitools.util import (
        calc_tags,
        tag_image,
        )
    from amitools import ec2connect
    if args.create_date is None:
        when = datetime.datetime.utcfromtimestamp(args.create_timestamp)
    else:
        assert args.create_timestamp is None, args.create_timestamp
        when = dateparse(args.create_date)
    conn = ec2connect(args.region)
    tags = calc_tags(
        args.source_image,
        args.source_instance,
        args.source_region,
        when,
        )        
    tag_image(
        conn,
        args.image_id,
        tags,
        )
