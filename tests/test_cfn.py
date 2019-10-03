import mock
import os
import unittest

from nose2.tools import params

from sspad import cfn


BLACKLIST_SAMPLE = '\n'.join([
    '# garbage',      # Commented string
    ' ',              # Empty string
    '0123456789',     # Account blacklist
    'us-east-1',      # Region blacklist
    r'^us-west-\d+',  # Region blacklist regex
])
"""Sample contents of a blacklist file"""


class StackSet(unittest.TestCase):
    """
    Tests the sspad.cfn.StackSet object
    """
    @mock.patch('sspad.cfn.glob')
    @mock.patch('sspad.cfn.StackSet.FromPath')
    def test_FromAll(self, mock_FromPath, mock_glob):
        """
        Test that directory enumeration works
        """
        path = 'test-dir'
        suffix = '.test-suffix'
        test_stacks = [
            'stackset1' + suffix,
            'stackset2' + suffix,
        ]
        mock_glob.glob.return_value = test_stacks

        stacks = list(cfn.StackSet.FindAll(
            path,
            suffix))

        # Ensure the proper number of Stack Sets were found
        self.assertEqual(
            len(stacks),
            len(test_stacks),
            'Incorrect number of StackSets found')

        # Ensure FromPath is called the correct number of times
        self.assertEqual(
            mock_FromPath.call_count,
            len(test_stacks),
            'sspad.cfn.StackSet.FromPath called incorrect number of times')

    @mock.patch('sspad.cfn.os.path.exists')
    def test_FromPath_blacklist(self, patch_exists):
        """
        Tests blacklist reading
        """
        path = 'test-dir'
        suffix = '.test-suffix'
        stack_name = 'stackset1'
        blacklist_suffix = '.test-blacklist'
        global_suffix = '.test-global'

        # Indicate global and blacklist present
        patch_exists.return_value = True

        # Setup the StackSet class
        cfn.StackSet.blacklist_suffix = blacklist_suffix
        cfn.StackSet.global_suffix = global_suffix

        test_stack_path = os.path.join(path, stack_name + suffix)
        test_blacklist_path = os.path.join(path, stack_name + blacklist_suffix)

        with mock.patch('sspad.cfn.open',
                        mock.mock_open(read_data=BLACKLIST_SAMPLE),
                        create=True) as mock_open:

            # Attempt instantiating the StackSet
            stackset = cfn.StackSet.FromPath(test_stack_path)

            # Ensure the blacklist was opened
            mock_open.assert_called_once_with(test_blacklist_path)

            # Ensure the account was found in the blacklist
            self.assertEqual(
                stackset.account_blacklist,
                ['0123456789'],
                'StackSet.account_blacklist incorrect')

            # Ensure the two regions specs were found in the blacklist
            self.assertEqual(
                stackset.region_blacklist,
                [
                    'us-east-1',
                    r'^us-west-\d+',
                ],
                'StackSet.region_blacklist incorrect')

    @mock.patch('sspad.cfn.os.path.exists')
    def test_FromPath_instantiation(self, patch_exists):
        """
        Tests basic instantiation
        """
        path = 'test-dir'
        suffix = '.test-suffix'
        stack_name = 'stackset1'
        blacklist_suffix = '.test-blacklist'
        global_suffix = '.test-global'

        # Indicate not global and no blacklist present
        patch_exists.return_value = False

        # Setup the StackSet class
        cfn.StackSet.blacklist_suffix = blacklist_suffix
        cfn.StackSet.global_suffix = global_suffix

        # Attempt instantiating the StackSet
        test_stack_path = os.path.join(path, stack_name + suffix)
        stackset = cfn.StackSet.FromPath(test_stack_path)

        # Check the path
        self.assertEqual(
            stackset.path,
            test_stack_path,
            'StackSet.path incorrect')

        # Check the name
        self.assertEqual(
            stackset.name,
            stack_name,
            'StackSet.name incorrect')

        # Ensure the blacklists are empty
        self.assertEqual(
            stackset.account_blacklist,
            [],
            'StackSet.account_blacklist should be empty')
        self.assertEqual(
            stackset.region_blacklist,
            [],
            'StackSet.region_blacklist should be empty')

    @params(
        (False,),
        (True,),
    )
    @mock.patch('sspad.cfn.os.path.exists')
    def test_FromPath_is_global(self, patch_is_global, patch_exists):
        """
        Tests that is_global check works
        """
        path = 'test-dir'
        suffix = '.test-suffix'
        stack_name = 'stackset1'
        blacklist_suffix = '.test-blacklist'
        global_suffix = '.test-global'

        # Override os.path.exists to indicate whether or not this is global
        patch_exists.return_value = patch_is_global

        # Setup the StackSet class
        cfn.StackSet.blacklist_suffix = blacklist_suffix
        cfn.StackSet.global_suffix = global_suffix

        with mock.patch('sspad.cfn.open',
                        mock.mock_open(read_data=BLACKLIST_SAMPLE),
                        create=True):
            # Attempt instantiating the StackSet
            stackset = cfn.StackSet.FromPath(
                os.path.join(path, stack_name + suffix))

            # Check the is_global attribute
            self.assertEqual(
                stackset.is_global,
                patch_is_global,
                'is_global check is broken')


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
