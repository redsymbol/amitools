import unittest
import os
import logging
from amitools import ec2connect

DEV_AMI = os.environ['AMITOOLS_DEV_AMI']
DEV_SG = os.environ.get('AMITOOLS_DEV_SG', 'dev')
DEV_KEYPAIR = os.environ.get('AMITOOLS_DEV_KEYPAIR', 'dev')
DEV_INSTANCE_TYPE='t1.micro'

def log(msg):
    import sys
    if not msg.endswith('\n'):
        msg += '\n'
    sys.__stdout__.write(msg)
    sys.__stdout__.flush()

class InstanceTestCase(unittest.TestCase):
    '''
    TestCase that runs an EC2 instance for you to operate on

    A single instance is run before any tests start; it will block
    until that instance is in the "running" state.  After all tests are run, the instance is terminated.

    Note that the same single instance is used for all tests (test_*
    methods) defined in this class; we don't start a new one in each
    test method, as a wall-clock-time optimization.

    Information on the (EC2) instance is stored in self.instance,
    which is an (Python class) instance of boto.ec2.instance.Instance.

    This reuses a lot of code in amitools, so bugs can prevent the
    instance from even running. This is probably more of a feature
    than a bug, because such failures will be noisy and obvious - just
    know to watch for it.  The only danger is in a failure to
    terminate the instance on teardown - if that happens and you don't
    terminate it manually, it will show up on your AWS bill.

    The setup also sets self.conn as a boto EC2 connection object, in
    case you need to query the boto API within your test or setup.

    INSTANCE PARAMETERS

    To run tests you will need to define an AMI ID to run, exporting
    it as AMITOOLS_DEV_AMI in the environment.  You will also need to
    define a security group and keypair, exported as AMITOOLS_DEV_SG
    and AMITOOLS_DEV_KEYPAIR respectively; if not set, the value "dev"
    will be used for each.

    TODO: can we make that optional? For many tests, setting a security group or keypair isn't necessary.

    '''

    # the EC2 instance - object of type boto.ec2.instance.Instance
    instance = None

    @classmethod
    def setupClass(cls):
        # silence boto's verbose debug logging, which can otherwise
        # produce hundreds of lines of output if a test fails
        cls.old_boto_loglevel = logging.getLogger('boto').level
        new_boto_loglevel = logging.CRITICAL
        log('Changing boto log level from "%s" to "%s" during tests' % (cls.old_boto_loglevel, new_boto_loglevel))
        logging.getLogger('boto').setLevel(new_boto_loglevel)
        
        from amitools.watch import EC2InstanceWatcher
        cls.conn = ec2connect()
        params = {
            'image_id'        : DEV_AMI,
            'security_groups' : [DEV_SG],
            'key_name'        : DEV_KEYPAIR,
            'instance_type'   : DEV_INSTANCE_TYPE,
            }
        log('Running instance with params: ' + str(params))
        reservation = cls.conn.run_instances(**params)
        assert len(reservation.instances) == 1, reservation.instances
        cls.instance = reservation.instances[0]
        log('Launched instance %s - blocking until it is running' % cls.instance.id)
        EC2InstanceWatcher(cls.instance.id, cls.conn).waiton('running')
        log('Dev instance %s in "running" state, ready for tests' % cls.instance.id)
    
    @classmethod
    def tearDownClass(cls):
        try:
            cls._tearDownClass()
        except:
            import sys
            sys.__stderr__.write('''**** WARNING This test may have failed to terminate a temporary EC2
**** instance it had run. You will have to manually look for and
**** terminate it. Be careful, or this may inflate your AWS bill!!!
''')
            sys.__stderr__.flush()
            raise

    @classmethod
    def _tearDownClass(cls):
        if cls.instance:
            log('\nTerminating instance %s' % cls.instance.id)
            terminated = cls.conn.terminate_instances(instance_ids=[cls.instance.id])
            assert len(terminated) == 1, terminated
            cls.instance = None
            logging.getLogger('boto').setLevel(cls.old_boto_loglevel)
        

