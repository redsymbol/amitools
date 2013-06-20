from amitools.test import InstanceTestCase

class TestTagImage(InstanceTestCase):
    def test_simple(self):
        # Start by creating our own AMI, which we'll do by imaging the dev instance
        from amitools.util import random_name
        from amitools.watch import EC2ImageWatcher
        self.log('Creating test AMI')
        image_id = self.conn.create_image(self.instance.id, random_name(), no_reboot=True)
        self.log('Test AMI id will be %s - waiting until it is available' % image_id)
        EC2ImageWatcher(image_id, self.conn).waiton('available')
        image = self.conn.get_all_images([image_id])[0]
        self.log('Test AMI %s available, proceeding with test ' % image_id)
        # now we have our own unique image with no tags
        self.assertEqual(0, len(image.tags), str(image.tags))
        from amitools.tools.ami_tag_image import (
            get_args,
            main,
            )
        args = get_args([
                '--source-image',
                'ami-12341234',
                '--source-instance',
                'i-12341234',
                '--source-region',
                'us-east-1',
                '--create-timestamp',
                '1369723137',
                image_id,
                ])
        result = main(args)

        # check result
        new_image = self.conn.get_all_images([image_id])[0]
        self.assertEqual('ami-12341234', new_image.tags['source_image'])
        self.assertEqual('i-12341234', new_image.tags['source_instance'])
        self.assertEqual('1369723137', new_image.tags['create_timestamp'])
        self.assertEqual('us-east-1', new_image.tags['source_region'])
            
