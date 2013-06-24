STATE_CHOICES = [
    'exists',
    'available',
    'pending',
    'failed',
    ]
def get_args():
    import argparse
    from amitools import common_argparser
    parser = argparse.ArgumentParser(
        description='Wait for an AMI to reach a particular state',
        epilog='',
        parents = [common_argparser],
        )
    parser.add_argument('image_id',
                        help='AMI ID')
    parser.add_argument('state', default='available', nargs='?', choices=STATE_CHOICES, 
                        help='State to wait for')
    parser.add_argument('--nowait-exists', default=False, action='store_true',
                        help='Don\'t wait for the image ID to exist before checking state')
    args = parser.parse_args()
    if not args.image_id.startswith('ami-'):
        parser.error('image_id must start with "ami-"')
    return args

def can_reach(prior_state, target_state):
    if prior_state == target_state:
        return True
    return 'pending' == prior_state

def main(args):
    from amitools import (
        EC2ImageWatcher,
        ec2connect,
        )
    from amitools.exceptions import TimeoutException
    conn = ec2connect(args.region)
    image_watcher = EC2ImageWatcher(args.image_id, conn)
    current_state = image_watcher.state()
    if current_state is None:
        if args.nowait_exists:
            return {
                'msg' : 'ERROR\tNo image ID {}'.format(args.image_id),
                'exit_code' : 1,
                }
        try:
            current_state = image_watcher.waiton_exists()
        except TimeoutException as ex:
            return {
                'msg' : 'FATAL\tTimed out waiting for image ID {} to exist'.format(args.image_id),
                'exit_code' : 2,
                }
    assert current_state is not None
    if 'exists' != args.state:
        if not can_reach(current_state, args.state):
            return {
                'msg' : 'FATAL\tCurrent state of "{}" can never transistion to target of "{}"'.format(current_state, args.state),
                'exit_code' : 3,
                }
        if current_state != args.state:
            try:
                image_watcher.waiton(args.state)
            except TimeoutException as ex:
                return {
                    'msg' : 'FATAL\tTimed out waiting for image ID {} to reach state {} - lastest was {}'.format(
                        args.image_id, args.state, current_state),
                    'exit_code' : 1,
                    }
