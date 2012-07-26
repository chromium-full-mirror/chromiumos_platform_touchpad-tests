# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module provides the TestFactory class to create new tests based upon
# an activity and cmt log.

from replay import Replay
from test_case import TestCase
import json

new_test_template = """\
# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

def Validate(raw, gestures, events):
  return False
"""

class TestFactory(object):
  """
  The TestFactory can create new test cases. Testa are named after their
  activity log filename. It will automatically trim the cmt log to match
  the activity logs time range.
  """

  user_property_names = []

  def __init__(self, tests_dir, replay_tool):
    self.tests_dir = tests_dir
    self.replay_tool = replay_tool

  def CreateTest(self, name, activity_file, cmt_file):
    """
    Create a new test. This method will create all necessary files to replay
    the events from the activity/cmt log file and also provides a template for
    the validator.
    """
    case = TestCase(self.tests_dir, name)
    activity = json.loads(open(activity_file).read())

    # extract from/to times from activity log
    hwstates = filter(lambda e: e["type"] == "hardwareState",
                      activity["entries"])
    trim_from = hwstates[0]["timestamp"]
    trim_to = hwstates[-1]["timestamp"]

    # extract user defined properties
    properties = activity["properties"]
    user_properties = {}
    for name in TestFactory.user_property_names:
      user_properties[name] = properties[name]
    json.dump({"gestures": user_properties}, open(case.case_property_file, "w"))

    # trim event log file
    replay = Replay(case.platform_dat_file, self.replay_tool)
    replay.Trim(cmt_file, case.log_file, trim_from, trim_to)

    # only create new module if this test case is not using the module
    # from commons
    if not case.module:
      open(case.case_module_file, "w").write(new_test_template)
    return case
