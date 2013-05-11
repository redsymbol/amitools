import unittest

class MockImage(object):
    def __init__(self, image_id, tags=None):
        self.id = image_id
        self.tags = tags or {}

class TestChain(unittest.TestCase):
    def test_build_chain(self):
        from amitools import build_chain
        all_images = [
            MockImage('ami-33333333', {'source_image' : 'ami-44444444'}),
            MockImage('ami-77777777', {'source_image' : 'ami-88888888'}),
            MockImage('ami-44444444', {'source_image' : 'ami-55555555'}),
            MockImage('ami-55555555', {'source_image' : 'ami-66666666'}),
            MockImage('ami-11111111', {'source_image' : 'ami-22222222'}),
            MockImage('ami-66666666', {'source_image' : 'ami-77777777'}),
            MockImage('ami-22222222', {'source_image' : 'ami-33333333'}),
            ]

        expected = [
            'ami-11111111',
            'ami-22222222',
            'ami-33333333',
            'ami-44444444',
            'ami-55555555',
            'ami-66666666',
            'ami-77777777',
            'ami-88888888',
            ]
        actual = build_chain('ami-11111111', all_images)
        self.assertSequenceEqual(expected, actual)
        
        expected = [
            'ami-44444444',
            'ami-55555555',
            'ami-66666666',
            'ami-77777777',
            'ami-88888888',
            ]
        actual = build_chain('ami-44444444', all_images)
        self.assertSequenceEqual(expected, actual)
