
#: Indicates successful program execution
CHAIN_SUCCESS = 0
#: Indicates the AMI we are looking for was not found
CHAIN_NO_AMI = 1

def get_args(argv=None):
    import argparse
    from amitools import common_argparser
    parser = argparse.ArgumentParser(
        description='Determine what images an image is derived from',
        epilog='',
        parents = [common_argparser],
        )
    parser.add_argument('image_id',
                        help='ID of AMI to find ancestry of')
    args = parser.parse_args(argv)
    if not args.image_id.startswith('ami-'):
        parser.error('image_id must start with "ami-"')
    return args

def main(args):
    from amitools import (
        ec2connect,
        build_chain,
        )
    conn = ec2connect(args.region)
    all_images = conn.get_all_images(filters={'tag-key':'source_image'})
    try:
        chain = build_chain(args.image_id, all_images)
        exit_code = CHAIN_SUCCESS
    except AssertionError:
        chain = []
        exit_code = CHAIN_NO_AMI
    return {
        'exit_code' : exit_code,
        'chain' : chain,
        }

