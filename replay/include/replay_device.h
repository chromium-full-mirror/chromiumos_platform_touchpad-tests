// Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef REPLAY_DEVICE_H_
#define REPLAY_DEVICE_H_

#include <string>
#include <vector>

#include <base/basictypes.h>
#include <gestures/gestures.h>

#include <evemu_device.h>
#include <generic_stream.h>
#include <libevdev_mock.h>

namespace replay {

// This structure contains all external configuration for the replay
// device. Including properties and all input/output streams for logs and
// settings.
struct ReplayDeviceConfig {
  // Enumeration of the different logs created by the simulation.
  enum LogCategory {
    // log created by libevdev
    kLogEvdev = 0,
    // log created by the gestures library
    kLogGestures,
    // json activity log generated at the end of a replay
    kLogActivity,
    // number of log categories.
    kLogCategoryCount
  };

  // Array containing all streams for log files
  GenericOStream log[ReplayDeviceConfig::kLogCategoryCount];

  // stream to the device data file
  GenericIStream device;
};

// The main class for replaying event logs. It can only be instantiated with a
// ReplayDeviceConfig instance that contains valid streams. It allows
// to replay events and observe the current state of the multitouch stack.
// It also contains an interface for the libevdev and gestures mock to
// handle functionality like timers and callbacks.
class ReplayDevice {
 public:
  // All instances are tracked and accessible via GetDevice to allow mock
  // methods to access instances without having a pointer to them.
  ReplayDevice(ReplayDeviceConfig* config);

  // Unregisters this instance automatically and it will no longer be accessible
  // via GetDevice.
  virtual ~ReplayDevice();

  // Replays all events from stream until the stream is empty.
  void ReplayEvents(GenericIStream* stream);

  // Replay a single input event.
  void ReplayEvent(const struct input_event& event);

  // Log a message to specified category. Used by mocks for logging.
  void Log(ReplayDeviceConfig::LogCategory category,
           const std::string& message);

  // The gestures library does have any means of identifying different devices
  // in the log method. It will use LogAll to log to all open instances of
  // ReplayDevice.
  static void LogAll(ReplayDeviceConfig::LogCategory category,
                     const std::string& message);

  // This method is to be called by libevdev when a syn event is processed.
  void SynCallback(EventStatePtr, struct timeval*);

  // Static method to access a device of a specific ID.
  static ReplayDevice* GetDevice(size_t id);

  EventStatePtr current_state() {
    return current_state_;
  }

  Evdev_* evdev_device() {
    return evdev_device_;
  }

  evemu::EvemuDevice* evemu_device() {
    return evemu_device_;
  }

 private:
  DISALLOW_COPY_AND_ASSIGN(ReplayDevice);

  // Reference to the configuration for accessing the streams.
  ReplayDeviceConfig* config_;

  // The id of this device, as used by GetDevice.
  int id_;

  // The EvemuDevice is used to read event/device files.
  evemu::EvemuDevice* evemu_device_;

  // Instances to the actual multitouch stack
  Evdev_* evdev_device_;

  // The current state of the multitouch stack
  EventStatePtr current_state_;

  // Array containing all instances of ReplayDevice.
  static std::vector<ReplayDevice*> devices_;
};

}  // namespace replay

#endif  // REPLAY_DEVICE_H_
