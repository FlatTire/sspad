"""
cfn
===
CloudFormation interactions
"""
import glob
import logging
import os
import re

#  from botocore.exceptions import ClientError


log = logging.getLogger(__name__)
"""Define a logger for handling output"""


class StackSet(object):
    _log = None
    blacklist_suffix = '.blacklist'
    global_suffix = '.global'

    @classmethod
    def FindAll(cls, path, suffix='.template', global_suffix=None,
                blacklist_suffix=None):
        """
        Yields a list of tuples of StackSets in a directory

        :param path: Directory
        :type path: str
        :param suffix: Suffix for template (ie. '.template')
        :type suffix: str
        :param global_suffix: Suffix to indicate global
        :type global_suffix: str
        :param blacklist_suffix: Suffix to define blacklist
        :type blacklist_suffix: str
        :rtype: StackSet
        :returns: StackSet instances
        """
        # Setup logging
        if cls._log is None:
            cls._log = logging.getLogger(cls.__name__)

        # Set the blacklist suffix
        cls.blacklist_suffix = blacklist_suffix or cls.blacklist_suffix

        # Set the global suffix
        cls.global_suffix = global_suffix or cls.global_suffix

        # Compose the path for the glob filter
        globpath = os.path.join(path, '*' + suffix)
        cls._log.debug(
            f'FindAll: Searching for StackSet templates: {globpath}')

        # Retain counters for how many stacks found
        found_global = 0
        found_regional = 0

        print('<debug>')
        print(glob.glob(globpath))
        print('</debug>')
        for template in glob.glob(globpath):
            found = cls.FromPath(template)

            # Increment counters
            if found.is_global:
                found_global += 1
            else:
                found_regional += 1

            yield found

        # Log the results
        log.debug(f'FindAll: Found global={found_global}'
                  f' regional={found_regional}')

    @classmethod
    def FromPath(cls, path):
        """
        Instantiates a new object based on template path

        :param path: Path to StackSet template
        :type path: str
        :rtype: StackSet
        :returns: New StackSet instance
        """
        new_stackset = cls()
        new_stackset.path = path

        # Remove the file extension
        new_stackset.prefix = os.path.splitext(new_stackset.path)[0]

        # Determine the basename
        new_stackset.name = os.path.basename(new_stackset.prefix)

        # Determine if flagged as global
        new_stackset.is_global = os.path.exists(
            new_stackset.prefix + cls.global_suffix)

        ###
        # Load the StackSet blacklist (if present)
        ###

        # Compose the path to the blacklist file
        blacklist_path = os.path.join(
            new_stackset.prefix + cls.blacklist_suffix)

        # If the blacklist does not exist for this StackSet, nothing will be
        # returned
        new_stackset.account_blacklist = []
        new_stackset.region_blacklist = []
        if os.path.exists(blacklist_path):
            # Define a pattern for matching account ids in blacklists
            account_pattern = re.compile(r'^\d+$')

            # Define a pattern for lines to ignore in blacklists
            ignore = re.compile(r'^\s*(#.*)?$')

            # Read in each line of the blacklist file
            with open(blacklist_path) as infile:
                # Load the first line
                line = infile.readline()

                while line:
                    # Strip whitespace before evaluating
                    line = line.strip()

                    if ignore.match(line):
                        # This is a line to be ignored

                        # Load the next line
                        line = infile.readline()
                        continue

                    elif account_pattern.match(line):
                        # This is an account to blacklist
                        new_stackset.account_blacklist.append(line)

                    else:
                        # This is a region or region regex
                        new_stackset.region_blacklist.append(line)

                    # Load the next line
                    line = infile.readline()

        ###
        # Return the build object
        ###
        return new_stackset

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name}>'

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
