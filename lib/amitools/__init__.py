import time

from .cl import (
    clsetup,
    common_argparser,
    )

from .watch import (
    EC2InstanceWatcher,
    EC2ImageWatcher,
    )
from dt import (
    datefmt,
    totimestamp,
    )

def ec2connect(region=None):
    import os
    from boto.ec2 import connect_to_region
    access_key = os.environ['AWS_ACCESS_KEY_ID']
    secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    region = region or os.environ['AWS_DEFAULT_REGION']
    return connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

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

