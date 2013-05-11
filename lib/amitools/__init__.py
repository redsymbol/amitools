import time

class AmitoolsException(Exception):
    pass
class TimeoutException(AmitoolsException):
    pass
class ImageNotFound(AmitoolsException):
    pass

import argparse
common_argparser = argparse.ArgumentParser(
    add_help=False,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
common_argparser.add_argument('-r', '--region', default=None,
                        help='''Specify REGION as the web service region to use.
Overrides the value specified by AWS_DEFAULT_REGION.
''')


def single_or_none(items):
    '''
    If the list items is empty, return None.
    If the list items has one element, return that element.
    If the list items has more than one element, trigger an AssertionError.
    '''
    assert len(items) <= 1, items
    if len(items) > 0:
        return items[0]
    return None

def get_instance(conn, instance_id):
    reservations = conn.get_all_instances([instance_id])
    instances = instances_of(reservations)
    return single_or_none(instances)

def instances_of(reservations):
    '''
    Fetch a list of all instances in a list of reservations

    Handy for translating the results of boto's
    EC2Connection.get_all_instances into a list of instances.
    
    '''
    return [instance
            for reservation in reservations
            for instance in reservation.instances
            ]

class ResourceWatcher(object):
    # time in seconds to wait between polls
    WAIT = 10
    # How long to wait before giving up, in seconds
    TIMEOUT = 5 * 60
    # Optionally define to have subclass automatically assert resource ID has a certain prefix
    RESOURCE_PREFIX = None
    
    def __init__(self, resource_id, conn):
        if self.RESOURCE_PREFIX:
            assert resource_id.startswith(self.RESOURCE_PREFIX), resource_id
        self.resource_id = resource_id
        self.resource = None
        self.conn = conn
        
    def waiton_exists(self):
        state = self.state()
        deadline = time.time() + self.TIMEOUT
        while state is None:
            time.sleep(self.WAIT)
            if time.time() > deadline:
                raise TimeoutException(self.resource_id)
            state = self.state()
        return state
            
    def waiton(self, target_state):
        state = self.waiton_exists()
        deadline = time.time() + self.TIMEOUT
        while state != target_state:
            time.sleep(self.WAIT)
            if time.time() > deadline:
                raise TimeoutException(self.resource_id)
            state = self.state()
        return state
            
    def state(self):
        '''
        Contract:
          If the resource with the given ID exists, return its state.
          If the resource does NOT exist, return None.
          
        '''
        self.update_resource()
        if self.resource:
            current_state = self.resource.state
        else:
            current_state = None
        return current_state

    def update_resource(self):
        '''
        Freshly get the relevant resource object, set to self.resource

        If the resource does not exist, set self.resource to None
        '''
        assert False, 'subclass must implement'

class EC2InstanceWatcher(ResourceWatcher):
    RESOURCE_PREFIX = 'i-'
    def update_resource(self):
        reservations = self.conn.get_all_instances([self.resource_id])
        instances = instances_of(reservations)
        self.resource = single_or_none(instances)

class EC2ImageWatcher(ResourceWatcher):
    RESOURCE_PREFIX = 'ami-'
    def update_resource(self):
        from boto.exception import EC2ResponseError
        self.resource = None
        try:
            images = self.conn.get_all_images([self.resource_id])
        except EC2ResponseError as ex:
            if 'InvalidAMIID.NotFound' != ex.error_code:
                raise
        else:
            self.resource = single_or_none(images)

def random_name(prefix=None):
    import time
    from random import randint
    from sys import maxsize
    prefix = prefix or 'AMI'
    return '{}-{}-{}'.format(
        prefix,
        int(time.time()),
        randint(maxsize >> 3, maxsize),
        )

def sigint_exit(signum, frame):
    import sys
    sys.stderr.write('\n')
    sys.exit(1)

def clsetup():
    import signal
    signal.signal(signal.SIGINT, sigint_exit)

def ec2connect(region=None):
    import os
    from boto.ec2 import connect_to_region
    access_key = os.environ['AWS_ACCESS_KEY_ID']
    secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    region = region or os.environ['AWS_DEFAULT_REGION']
    return connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

DATETIME_F = ''.join([
        # 20110909T233600Z
        '%Y',
        '%m',
        '%d',
        'T',
        '%H',
        '%M',
        '%S',
        'Z',
        ])

def datefmt(dt):
    return dt.strftime(DATETIME_F)

def dateparse(dt_str):
    import datetime
    return datetime.datetime.strptime(dt_str, DATETIME_F)

def totimestamp(dt):
    from calendar import timegm
    return timegm(dt.timetuple())

def tag_image(conn, image_id, source_image_id, source_instance_id, when):
    '''
    conn               : boto.ec2.connection.EC2Connection
    image_id           : AMI ID
    source_image_id    : str
    source_instance_id : str
    when               : datetime.datetime
    '''
    tags = {
        'source_image'     : source_image_id,
        'source_instance'  : source_instance_id,
        'create_date'      : datefmt(when),
        'create_timestamp' : totimestamp(when),
        }
    conn.create_tags([image_id], tags)

def build_chain(start_image_id, images):
    images_by_id = dict(
        (image.id, image)
        for image in images)
    assert start_image_id in images_by_id, start_image_id
    start_image = images_by_id[start_image_id]
    image_source_map = dict(
        (image.id, image.tags['source_image'])
        for image in images)
    assert start_image.id in image_source_map
    chain = [start_image.id]
    current_id = start_image.id
    while True:
        try:
            next_image_id = image_source_map[current_id]
        except KeyError:
            break
        chain.append(next_image_id)
        current_id = next_image_id
    return chain

