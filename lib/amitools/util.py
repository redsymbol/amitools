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

def tag_image(conn, image_id, source_image_id, source_instance_id, when):
    '''
    conn               : boto.ec2.connection.EC2Connection
    image_id           : AMI ID
    source_image_id    : str
    source_instance_id : str
    when               : datetime.datetime
    '''
    from .dt import (
        datefmt,
        totimestamp,
        )
    tags = {
        'source_image'     : source_image_id,
        'source_instance'  : source_instance_id,
        'create_date'      : datefmt(when),
        'create_timestamp' : totimestamp(when),
        }
    conn.create_tags([image_id], tags)
