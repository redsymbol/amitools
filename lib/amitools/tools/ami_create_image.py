def get_args(argv=None):
    import argparse
    from amitools import common_argparser
    parser = argparse.ArgumentParser(
        description='ami-create-image - Like ec2-create-image, but way better',
        parents = [common_argparser],
        epilog='''By default, a random name is generated for the AMI. You can supply
a prefix with -N/--random-name-prefix, or an explicit name with
 -n/--name.
'''
        )
    parser.add_argument('instance_id',
                        help='Instance ID to create image from')
    parser.add_argument('-n', '--name', default=None,
                        help='Name of the image')
    parser.add_argument('-N', '--random-name-prefix',
                        help='Prefix for random name of an image')
    parser.add_argument('-d', '--description', default=None,
                        help='Description of the image')
    parser.add_argument('--no-reboot', default=False, action='store_true',
                        help='If specified, the instance will not be rebooted during the bundle process.')
    # parser.add_argument('-b', '--block-device-mapping', default=None,
    #                     help='')
    args = parser.parse_args(argv)
    if not args.instance_id.startswith('i-'):
        parser.error('instance_id must start with "i-"')
    return args

def main(args):
    import datetime
    import time
    from amitools.watch import EC2ImageWatcher
    from amitools.util import (
        get_instance,
        random_name,
        )
    from amitools import ec2connect
    from amitools.util import (
        calc_tags,
        tag_image,
        )
    
    if args.name is None:
        args.name = random_name(args.random_name_prefix)
        
    conn = ec2connect(args.region)
    
    image_id = conn.create_image(
        args.instance_id,
        args.name,
        description=args.description,
        no_reboot = args.no_reboot,
        )
    image_watcher = EC2ImageWatcher(image_id, conn)
    image_watcher.waiton_exists()
    # AMI image creation started. While that's cooking, set up tags
    image = image_watcher.resource
    source_instance = get_instance(conn, args.instance_id)
    tags = calc_tags(
        source_instance.image_id,
        args.instance_id,
        datetime.datetime.utcnow(),
        )        
    tag_image(
        conn,
        image.id,
        tags,
        )
    return {
        'image_id' : image_id,
        }
    
