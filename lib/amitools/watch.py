import time
from .exceptions import TimeoutException
from .util import (
    single_or_none,
    instances_of,
    )

class ResourceWatcher(object):
    # time in seconds to wait between polls
    WAIT = 10
    # How long to wait before giving up, in seconds
    TIMEOUT = 5 * 60
    # Optionally define to have subclass automatically assert resource ID has a certain prefix
    RESOURCE_PREFIX = None
    # If defined, as a set of strings, waiton will verify target state is one of these values
    STATES = None

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
        assert target_state != 'exists', 'Use waiton_exists() instead to wait until the image exists'
        if self.STATES:
            assert target_state in self.STATES, target_state
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
    STATES = {
        'available',
        'pending',
        'failed',
        }
    
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

