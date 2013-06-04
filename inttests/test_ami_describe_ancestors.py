from amitools.test import InstanceTestCase

class TestDescribeAncestors(InstanceTestCase):
    def get_image(self, image_id):
        return self.conn.get_all_images([image_id])[0]
    
    def test_simple(self):
        import datetime
        from amitools.tools.ami_describe_ancestors import (
            get_args,
            main,
            CHAIN_SUCCESS,
            CHAIN_NO_AMI,
            )
        from amitools.util import (
            calc_tags,
            tag_image,
            )
        # Start by creating test AMIs
        from amitools.util import random_name
        from amitools.watch import EC2ImageWatcher
        self.log('Creating test AMIs')
        now = datetime.datetime.utcnow()
        # child AMI
        child_image_id = self.conn.create_image(self.instance.id, random_name(), no_reboot=True)
        self.log('Test child AMI id will be {} - setting up tags'.format(child_image_id))
        child_tags = calc_tags(
            self.instance.image_id,
            self.instance.id,
            now - datetime.timedelta(seconds=5),
            )
        child_watcher = EC2ImageWatcher(child_image_id, self.conn)
        child_watcher.waiton_exists()
        tag_image(self.conn, child_image_id, child_tags)
        self.log('Waiting for child AMI {} to be available'.format(child_image_id))
        child_watcher.waiton('available')
        # grandchild AMI
        grandchild_image_id = self.conn.create_image(self.instance.id, random_name(), no_reboot=True)
        self.log('Grandchild AMI ID will be {} - setting up tags'.format(grandchild_image_id))
        grandchild_tags = calc_tags(
            child_image_id,
            'i-12345678',
            now,
            )
        grandchild_watcher = EC2ImageWatcher(grandchild_image_id, self.conn)
        grandchild_watcher.waiton_exists()
        tag_image(self.conn, grandchild_image_id, grandchild_tags)
        self.log('Waiting for grandchild AMI {} to be available'.format(grandchild_image_id))
        grandchild_watcher.waiton('available')
        child_image = self.get_image(child_image_id)
        grandchild_image = self.get_image(grandchild_image_id)
        # now ready to run tests
        self.log('Test AMIs available, proceeding with test')
        args = get_args([
                grandchild_image_id,
                ])
        result = main(args)
        self.assertEqual(CHAIN_SUCCESS, result['exit_code'])
        expected_chain = [
            grandchild_image_id,
            child_image_id,
            self.instance.image_id,
            ]
        self.assertSequenceEqual(expected_chain, result['chain'])
        
