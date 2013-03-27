# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module contains the TestCase class which gives access to the data files
# belonging to a test case and validation that the TestCase has all required
# information.
from gesture_log import GestureLog
from os import path
from xorg_parser import XorgInputClassParser
import fnmatch
import imp
import json
import os
import traceback

class TestCase(object):
  """
  The TestCase class is constructed with test name and a tests directory.
  In order to automatically load properties from xorg config files, the
  xorg_conf_path argument has to be set to the path of the folder containing
  the chromeos xorg configuration files.

  Tests have multiple files associated with them and these file paths are
  determined using the convention over configuration paradigm:

  The tests directory contains one folder for each platform (lumpy, cr48, etc)
  as well as a common folder which is shared by all platforms. Each platform
  has to contain a platform.dat containing the platforms touchpad description
  (see replay tool and evemu). Additionally it can provide a platform.props file
  to pass properties to the gestures library.
  Each platform can organize test cases in subfolders.

  A test case is defined by a log file containing the event log and the name
  $(testname).log.
  The gestures from the log are validated using the python module in the same
  folder $(testname).py. If such a file cannot be found, the class will look for
  a file $(testname).py in same subdirectory of the common folder.

  Each test case can define parameters for the gestures library using a JSON
  file called $(testname).props. These properties override any properties set
  in platform.props.

  To make sure all those files are present and the test can be executed this
  class provides a method called Check which will return an error message
  in case there is an error.

  Tests are basically named after the path to the tests log file (including the
  platform name) but excluding the .log extension. So the log file
  $(tests_dir)/lumpy/categyoryA/testB.log has the name lumpy/categoryA/testB
  """
  _platform_dat = "platform.dat"
  _platform_props = "platform.props"
  _common_folder = "common"

  def __init__(self, tests_path, log_file_or_name, xorg_conf_path=None):
    self.tests_path = tests_path
    self.xorg_conf_path = xorg_conf_path
    self.xorg_parser = XorgInputClassParser()
    self._ignore_properties = []

    if not log_file_or_name.endswith(".log"):
      log_file = log_file_or_name + ".log"
    else:
      log_file = log_file_or_name

    (log_path, filename) = path.split(log_file)
    self.testname = path.splitext(filename)[0]
    self.path = log_path.split(os.sep)
    self.path.append(self.testname)
    self.properties = None

  def Check(self):
    """
    Returns an error message describing the configuration error, or True if
    the test can be executed.
    """
    if not path.exists(self.log_file):
      return self.log_file + " does not exist"

    # catch all errors caused by loading the module
    try:
      if self.module is None:
        return "cannot find module file"
    except:
      return "unable to load module\n" + traceback.format_exc()

    if "Validate" not in self.module.__dict__:
      return self.module.__file__ + " does not contain a Validate() method"

    return True

  def __str__(self):
    return self.name

  def __repr__(self):
    return self.name

  @property
  def name(self):
    return "/".join(self.path)

  @property
  def platform_name(self):
    return self.path[0]

  @property
  def platform_dat_file(self):
    return self._PlatformFile(self._platform_dat)

  @property
  def log_file(self):
    return self._TestCaseFile(".log")

  @property
  def case_module_file(self):
    return self._TestCaseFile(".py")

  @property
  def common_module_file(self):
    return self._CommonFile(".py")

  @property
  def case_property_file(self):
    return self._TestCaseFile(".props")

  @property
  def device_property_file(self):
    return self._PlatformFile("platform.props")

  @property
  def common_property_file(self):
    return self._CommonFile(".props")

  @property
  def description(self):
    module = self.module
    return module.Validate.__doc__ if module.Validate.__doc__ else ""

  @property
  def disabled(self):
    module = self.module
    return hasattr(module.Validate, "disabled") and module.Validate.disabled

  @property
  def module(self):
    module_file = self.case_module_file
    if not path.exists(module_file):
      module_file = self.common_module_file
    if not path.exists(module_file):
      return None

    return imp.load_source("validator", module_file)

  @property
  def gesture_props(self):
    if self.properties is None:
      self._LoadProperties()
    return self.properties["gestures"]

  @property
  def validator_props(self):
    if self.properties is None:
      self._LoadProperties()
    return self.properties["validator"]

  @property
  def ignore_properties(self):
    if self.properties is None:
      self._LoadProperties()
    return self._ignore_properties

  def _LoadProperties(self):
    self.properties = { "gestures": {}, "validator": {}}
    self._LoadXOrgConfigProperties(self._PlatformFile("platform.props"))
    self._LoadPropertiesFile(self._PlatformFile("platform.props"))
    self._LoadPropertiesFile(self._CommonFile(".props"))
    self._LoadPropertiesFile(self._TestCaseFile(".props"))
    self._ApplyIgnoreProperties()

  def _ApplyIgnoreProperties(self):
    for key in self._ignore_properties:
      if key in self.properties["gestures"]:
        del self.properties["gestures"][key]

  def _LoadXOrgConfigProperties(self, file):
    if not path.exists(file):
      return
    data = json.load(open(file, "r"))
    if self.xorg_conf_path and "xorg" in data and "file" in data["xorg"]:
      # TODO(denniskempin): error handling in general. Don't use exceptions
      # checking user provided data.
      filename = os.path.join(self.xorg_conf_path, data["xorg"]["file"])
      input_classes = self.xorg_parser.Parse(file=filename)
      if "identifier" in data["xorg"]:
        properties = input_classes[data["xorg"]["identifier"]]
        self.properties["gestures"].update(properties)
      if "identifiers" in data["xorg"]:
        for identifier in data["xorg"]["identifiers"]:
          properties = input_classes[identifier]
          self.properties["gestures"].update(properties)

  def _LoadPropertiesFile(self, file):
    if not path.exists(file):
      return
    data = json.load(open(file, "r"))
    if "gestures" in data:
      self.properties["gestures"].update(data["gestures"])
    if "validator" in data:
      self.properties["validator"].update(data["validator"])
    if "ignore" in data:
      self._ignore_properties.extend(data["ignore"])

  def _TestCaseFile(self, extension):
    return os.path.join(self.tests_path, *self.path) + extension

  def _CommonFile(self, extension):
    return os.path.join(self.tests_path, self._common_folder, *self.path[1:]) \
           + extension

  def _PlatformFile(self, filename):
    return os.path.join(self.tests_path, self.path[0], filename)
