import mock
import unittest

from nose2.tools import params

from sspad import cfg


class Config(unittest.TestCase):
    """
    Tests the sspad.cfg.Config object
    """

    SAMPLE_CONFIG = {
        'default_global_region': 'us-east-1',
        'default_regions': [
            '^us-.+',
        ],
        'stackset_region': 'us-east-1',
        'stackset_template_dir': 'stacksets',
    }

    SAMPLE_REGIONS = [
        'ap-northeast-1',
        'ap-northeast-2',
        'ap-south-1',
        'ap-southeast-1',
        'ap-southeast-2',
        'ca-central-1',
        'eu-central-1',
        'eu-north-1',
        'eu-west-1',
        'eu-west-2',
        'eu-west-3',
        'sa-east-1',
        'us-east-1',
        'us-east-2',
        'us-west-1',
        'us-west-2',
    ]

    @params(
        (['^us-(east|west)-1$'], ['us-east-1', 'us-west-1']),
        (['ca-central-1'], ['ca-central-1'])
    )
    def test_get_default_regions(self, cfg_default_regions, expected):
        """
        Test the default region filtering
        """
        # Setup the mock client
        ec2_client = mock.Mock()
        ec2_client.describe_regions.return_value = {
            'Regions': [
                {
                    'Endpoint': f'https://{region}.amazonaws.com',
                    'RegionName': region,
                    'OptInStatus': 'opt-in-not-required'
                }
                for region in self.SAMPLE_REGIONS
            ],
        }

        # Instantiate the config
        test_cfg = cfg.Config.FromDict(self.SAMPLE_CONFIG)

        # Override the Config.default_regions
        test_cfg.default_regions = cfg_default_regions

        # Test the default region filtering works appropriately
        self.assertEqual(
            set(test_cfg.get_default_regions(ec2_client)),
            set(expected),
            'Config.get_default_regions incorrect')

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
