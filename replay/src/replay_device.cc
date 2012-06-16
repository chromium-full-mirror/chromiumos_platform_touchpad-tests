// Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <replay_device.h>

#include <iomanip>
#include <iostream>

#include <libevdev_mock.h>

namespace replay {

std::vector<ReplayDevice*> ReplayDevice::devices_;

ReplayDevice::ReplayDevice(ReplayDeviceConfig* config)
    : config_(config), evemu_device_(NULL), current_state_(NULL) {
  id_ = devices_.size();
  devices_.push_back(this);

  // read device file into evemu
  evemu_device_ = new evemu::EvemuDevice();
  evemu_device_->ReadDeviceFile(config_->device.GetStream());

  // create libevdev mock
  evdev_device_ = NewEvdevMock(id_);
}

ReplayDevice::~ReplayDevice() {
  devices_[id_] = NULL;
}

void ReplayDevice::ReplayEvents(GenericIStream* stream) {
  struct input_event event;
  while (evemu_device_->ReadEvent(stream->GetStream(), &event) > 0) {
    ReplayEvent(event);
  }
}

void ReplayDevice::ReplayEvent(const struct input_event& event) {
  // Passing to C API. Drop const qualifier.
  Event_Process(evdev_device_, const_cast<struct input_event*>(&event));
}

void ReplayDevice::Log(ReplayDeviceConfig::LogCategory category,
                       const std::string& message) {
  GenericStream<std::ostream>& stream = config_->log[category];
  if (stream.Good()) {
    (*stream.GetStream()) << message;
    stream.GetStream()->flush();
  }
}

void ReplayDevice::LogAll(ReplayDeviceConfig::LogCategory category,
                          const std::string& message) {
  for (size_t i = 0; i < devices_.size(); ++i) {
    if (devices_[i]) {
      devices_[i]->Log(category, message);
    }
  }
}

void ReplayDevice::SynCallback(EventStatePtr evstate, struct timeval* timeval) {
}

ReplayDevice* ReplayDevice::GetDevice(size_t id) {
  assert(id < devices_.size());
  assert(devices_[id] != NULL);
  return devices_[id];
}

}  // namespace replay
