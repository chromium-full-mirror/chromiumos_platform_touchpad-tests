# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module provides the test runner which is responsible for discovering
# and executing tests.
from cStringIO import StringIO
import fnmatch
import json
import multiprocessing
import os
import sys
import traceback

from gesture_log import GestureLog
from mtreplay import MTReplay
from os import path
from test_case import TestCase

class TestRunner(object):
  """
  The TestRunner provides a simple interface to execute a set of test cases.
  All test results are returned in a result structure containing logs,
  validation results, errors, the generated gestures and the final score.
  """
  def __init__(self, tests_dir, xorg_conf_path=None):
    self.tests_dir = tests_dir
    self.xorg_conf_path = xorg_conf_path

  def RunTest(self, test_case):
    """
    This method executes a single test. The results are provided in the
    following structure:

    {
      "logs": {
        "evdev": ""       # libevdev logs
        "gestures": "",   # gestures library logs
        "activity": "",   # generated activity log
        "validation": ""  # logs from the validation process
      },
      "error": "",        # error message if applicable.
      "events": "",       # string representation of all events generated
      "gestures": "",     # string representation of all gestures generated
      "result": "",       # "success" the test provides a score.
                          # "failure" the test executed, but validation failed.
                          # "error" the test could not be executed.
      "score": 0          # the final score of the test
    }
    """
    out = {
      "logs": {
        "evdev": "",
        "gestures": "",
        "activity": "",
        "validation": ""
      },
      "error": "",
      "events": "",
      "description": "",
      "disabled": False,
      "gestures": "",
      "result": "",
      "score": 0
    }

    result = test_case.Check()
    if result is not True:
      out["error"] = result
      out["result"] = "error"
      return out

    out["description"] = test_case.description

    if test_case.disabled:
      out["disabled"] = True
      return out

    try:
      properties = json.dumps(test_case.gesture_props)
      replay = MTReplay(test_case.platform_dat_file, test_case.device_class)
      log = GestureLog(replay.Replay(test_case.log_file, properties, True))

      out["logs"]["evdev"] = replay.evdev_log
      out["logs"]["gestures"] = replay.gestures_log
      out["logs"]["activity"] = replay.activity_log
      out["events"] = "\n".join(map(lambda e: str(e), log.events))
      out["gestures"] = "\n".join(map(lambda g: str(g), log.gestures))

      # look for errors in the gestures library output
      errors = []
      for line in replay.gestures_log.splitlines():
        if line.startswith("ERROR:"):
          errors.append(line)

      if errors:
        out["error"] = "\n".join(errors)
        out["result"] = "error"
        return out

      # validate the replay results
      score, validation_log = test_case.module.Validate(log.raw,
          log.events, log.gestures)

      out["logs"]["validation"] = validation_log
      out["result"] = "success" if score is not False else "failure"
      out["score"] = score

    except:
      out["error"] = traceback.format_exc()
      out["result"] = "error"

    return out

  def RunGDB(self, glob):
    test_case = self.DiscoverTestCases(glob)[0]
    properties = json.dumps(test_case.gesture_props)
    replay = MTReplay(test_case.platform_dat_file, test_case.device_class)
    replay.Replay(test_case.log_file, properties, True, gdb_mode=True)

  def RunAll(self, glob="all"):
    """
    This method runs a set of test cases. Test cases can be selected using
    a unix-style GLOB or "all" to execute all tests.
    The result is a dictionary mapping the test name to the results structure
    as described in RunTest.
    """
    results = {}
    for case in self.DiscoverTestCases(glob):
      results[case.name] = self.RunTest(case)
    return results

  def DiscoverTestCases(self, glob=None):
    """
    Returns a list of test cases that matching the glob.
    """
    def ListDirRecursive(rootdir, sub_path=""):
      result = []
      for file in os.listdir(path.join(rootdir, sub_path)):
        if file[0] == ".":
          continue
        if path.isdir(path.join(rootdir, sub_path, file)):
          result.extend(ListDirRecursive(rootdir, path.join(sub_path, file)))
        else:
          result.append(path.join(sub_path, file))
      return result

    all_cases = []
    for platform in self._DiscoverPlatforms():
      files = ListDirRecursive(self.tests_dir, platform)
      log_files = fnmatch.filter(files, "*.log")
      test_cases = map(lambda f: TestCase(self.tests_dir, f,
                                          self.xorg_conf_path),
                       log_files)
      all_cases.extend(test_cases)

    if glob is not None and glob != "all":
      all_cases = filter(lambda c: fnmatch.fnmatch(c.name, glob), all_cases)

    return all_cases

  def _DiscoverPlatforms(self):
    def is_platform(platform):
      return path.isdir(path.join(self.tests_dir, platform)) and \
             path.exists(path.join(self.tests_dir, platform, "platform.dat"))
    return filter(is_platform, os.listdir(self.tests_dir))


def ParallelTestRunnerProcess(case):
  runner = TestRunner(case.tests_path)
  return (case, runner.RunTest(case))


class ParallelTestRunner(TestRunner):
  def RunAll(self, glob="all"):
    """
    Extends TestRunner.RunAll by multiprocessing. The test cases are distributed
    to as many processes as there are cores available.
    """
    pool = multiprocessing.Pool()
    cases = self.DiscoverTestCases(glob)
    data = pool.map(ParallelTestRunnerProcess, cases)
    pool.terminate()
    results = {}
    for case, result in data:
      results[case.name] = result

    return results
