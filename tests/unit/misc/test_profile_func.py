# Tai Sakuma <tai.sakuma@gmail.com>
import os

import pytest

import unittest.mock as mock

from alphatwirl.misc import profile_func, print_profile_func

##__________________________________________________________________||
def test_profile_func():
    func = mock.Mock()
    profile_func(func)

##__________________________________________________________________||
def test_print_profile_func(tmpdir_factory):
    tmpdir = str(tmpdir_factory.mktemp('misc'))
    func = mock.Mock()
    print(tmpdir)
    profile_out_path = os.path.join(tmpdir, 'profile.txt')
    print_profile_func(func, profile_out_path=profile_out_path)

##__________________________________________________________________||
