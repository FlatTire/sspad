"""
cfg
===
Configuration management module
"""
import re
import yaml


class Config(object):
    @classmethod
    def FromFile(cls, path):
        """
        Read in configuration from a file path

        :param path: Path to config file
        :type path: str
        :rtype: dict
        :returns: Hash of configuration options
        """
        with open(path, 'r') as infile:
            return cls.FromDict(yaml.safe(infile))

    @classmethod
    def FromDict(cls, from_dict):
        """
        Instantiate a configuration from a dict

        :param from_dict: Configuration data
        :type from_dict: dict
        :returns: Configuration
        :rtype: Config
        """
        new_cfg = cls()
        # TODO validate the schema of the config
        new_cfg.__dict__.update(from_dict)

        # Return the instantiated object
        return new_cfg

    def get_default_regions(self, ec2_client):
        """
        Find default regions

        :param ec2_client: boto3 EC2 client
        :type ec2_client: TODO
        :returns: List of all regions to use
        :rtype: list(str)
        """
        return [
            r['RegionName'] for r in
            ec2_client.describe_regions()['Regions']
            if any([
                re.search(region_spec, r['RegionName'])
                for region_spec in self.default_regions
            ])
        ]

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
