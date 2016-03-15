#!/usr/bin/env python
# @xzhou
# This tool is used to find unnecessary permissions used in our system services.
#
# The tool uses static analysis and:
# 1. Find all the permission declared by the application.
# 2. For each permission, we search if the corresponding api is called by using the api_permission mapping.
# 3. Output the permissions that is not used in the app.

import argparse
from androguard.core.bytecodes import apk, dvm
from androguard.core.analysis import analysis
from androlyze import AnalyzeAPK


class DeprivException(Exception):
    pass


class ApkDeprivilege:
    def __init__(self, verbose=False):
        self.apk_file_path = None
        # the apk representation
        self.apk = None
        self.dex = None
        self.dx = None
        self.declared_permissions = None

        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def load_apk(self, apk_file_path):
        '''
        Load the apk files and and inflate the apk, dex and dx structure
        Parameters
        ----------
        apk_file_path: The path of the apk file

        Returns: None
        -------
        '''
        self.log('loading %s, ...' % apk_file_path)
        self.apk_file_path = apk_file_path
        self.apk, self.dex, self.dx = AnalyzeAPK(self.apk_file_path)
        self.log('%s loaded' % self.apk.get_package())

    def find_dx_permissions(self):
        '''
        Find all permission that is used.
        Returns: None
        '''
        if self.dx:
            return analysis.get_dx_permissions(self.dx)
        else:
            raise DeprivException('apk file not loaded')

    def find_all_permission(self):
        '''Find all permission that is used by an application.'''
        if not self.apk:
            raise DeprivException('apk file not loaded')

        self.declared_permissions = self.apk.get_permissions()
        return self.declared_permissions

    def unnecessary_permission(self):
        declared_perm = self.find_all_permission()
        dx_perm, print_str = self.find_dx_permissions()

        result = []
        for p in declared_perm:
            p_str = str(p)
            perm = p_str.split('.')[-1]
            if perm not in dx_perm:
                print '[-]', p
                result.append(p)
            else:
                print '[+]', p
        return result

    def is_permission_used(self, permission):
        '''Check if this permission is used in the apk file.
        The idea is to find all the system api or system calls that use this permission, if not used,
        then it might be over privileged.
        '''
        # get the targeted version, we can only analyze sdk 22 for now
        # TODO check all versions
        target_sdk_version = min(self.apk.get_target_sdk_version(), 22)
        api_permission_mapping = self.load_api_permission_mapping(target_sdk_version)
        # reverse
        permission_api_mapping = self.inverse_mapping(api_permission_mapping, permission)
        print(permission_api_mapping)
        return False

    def analyze(self, apk_file):
        self.load_apk(apk_file)
        self.find_all_permission()
        unused_permission = self.unnecessary_permission()

        '''
        print '------\nthe following permissions is not necessary:'
        for p in unused_permission:
            print(p)
        '''

    def load_api_permission_mapping(self, sdk_version):
        package_name = 'androguard.core.api_specific_resources.api_permission_mappings'
        module_name = 'api_permission_mappings_api' + str(sdk_version)
        full_module_name = '.'.join([package_name, module_name])
        mapping = None
        try:
            mod = __import__(full_module_name, globals(),
                             locals(), ['AOSP_PERMISSIONS_BY_METHODS'], -1)
            mapping = mod.AOSP_PERMISSIONS_BY_METHODS
        except ImportError as e:
            print(e)
        return mapping

    def inverse_mapping(self, m, permission):
        '''return the apis that needs a permission.'''
        inv_m = {}
        for k, v in m.iteritems():
            if permission in v:
                inv_m[permission] = inv_m.get(permission, [])
                inv_m[permission].append(k)
        return inv_m

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Android application permission checking')
    parser.add_argument('apk', help='the apk files that need to be analyzed')
    parser.add_argument('-v', '--verbose', help='print message', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        print('The apk file is %s' % args.apk)

    analyzer = ApkDeprivilege(verbose=True)
    analyzer.analyze(args.apk)


