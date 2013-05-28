from amitools.test import InstanceTestCase

class TestCreateImage(InstanceTestCase):
    def test_simple(self):
        from amitools.test import DEV_AMI
        from amitools.tools.ami_create_image import (
            get_args,
            main,
            )
        args = get_args([
                self.instance.id,
                ])
        result = main(args)
        self.assertTrue('image_id' in result, result)
        image = self.conn.get_all_images([result['image_id']])[0]
        self.assertEqual(image.tags['source_instance'], self.instance.id)
        self.assertEqual(image.tags['source_image'], DEV_AMI)
