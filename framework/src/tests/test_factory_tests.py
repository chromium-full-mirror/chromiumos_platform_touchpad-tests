# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module contains unit tests for TestFactory
from os import path
from test_factory import TestFactory
from test_runner import TestRunner
import os
import unittest

tests_path = path.join(path.dirname(__file__), "testsdir")
replay_tool = path.join(path.dirname(__file__), "../../../replay/build/replay")

activity_file = path.splitext(__file__)[0] + "_activity.log"
cmt_file = path.splitext(__file__)[0] + "_cmt.log"

class TestFactoryTests(unittest.TestCase):
  """
  Unit tests for TestFactory. This test will add the activity log/cmt log next
  to this file to the test suite and then check if it can be discovered and
  the test definition is valid.
  """

  def test_new_case_discovery(self):
    factory = TestFactory(tests_path, replay_tool)
    factory.CreateTest("platform_a/added_test_case", activity_file, cmt_file)

    # test if the added test case is discovered
    cases = TestRunner(tests_path, replay_tool).DiscoverTestCases()
    case_names = map(lambda t: t.name, cases)
    self.assertTrue("platform_a/added_test_case" in case_names)

  def test_new_case_check(self):
    factory = TestFactory(tests_path, replay_tool)
    testcase = factory.CreateTest("platform_a/added_test_case", activity_file,
                                  cmt_file)
    testcase.Check()

  def tearDown(self):
    files = [path.join(tests_path, "platform_a/added_test_case.log"),
         path.join(tests_path, "platform_a/added_test_case.py"),
         path.join(tests_path, "platform_a/added_test_case.props")]
    for file in files:
      if os.path.exists(file):
        os.remove(file)


if __name__ == '__main__':
  unittest.main()
