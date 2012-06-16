// Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <trimmer.h>

#include <evemu_device.h>

namespace replay {

// Helper for bit operations
#define LONG_BITS (sizeof(long) * 8)
#define NLONGS(x) (((x) + LONG_BITS - 1) / LONG_BITS)

// Test for bit in an ulong array
static inline bool TestBit(int bit, unsigned long* array) {
  return !!(array[bit / LONG_BITS] & (1L << (bit % LONG_BITS)));
}

Trimmer::Trimmer(ReplayDevice* replay)
    : replay_(replay) {

}

void Trimmer::WriteEvent(GenericOStream* out, struct timeval& time, __u16 type,
                         __u16 code, __u32 value) {
  input_event event = { time, type, code, value };
  evemu::EvemuDevice::WriteEvent(out->GetStream(), event);
}
void Trimmer::WriteCurrentState(GenericOStream* out, struct input_event* syn) {
  EventStatePtr evstate = replay_->current_state();
  Evdev* device = replay_->evdev_device();

  // write slots
  for (int i = 0; i < evstate->slot_count; i++) {
    MtSlotPtr slot = &evstate->slots[i];
    if (slot->tracking_id == -1)
      continue;
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_SLOT, i);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_TOUCH_MAJOR, slot->touch_major);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_TOUCH_MINOR, slot->touch_minor);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_WIDTH_MAJOR, slot->width_major);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_WIDTH_MINOR, slot->width_minor);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_ORIENTATION, slot->orientation);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_POSITION_X, slot->position_x);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_POSITION_Y, slot->position_y);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_TOOL_TYPE, slot->tool_type);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_BLOB_ID, slot->blob_id);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_TRACKING_ID, slot->tracking_id);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_PRESSURE, slot->pressure);
    WriteEvent(out, syn->time, EV_ABS, ABS_MT_DISTANCE, slot->distance);
  }

  // write key state
  for (int i = 0; i < KEY_CNT; ++i) {
    if (TestBit(i, device->key_state_bitmask)) {
      WriteEvent(out, syn->time, EV_KEY, i, 1);
    }
  }
  evemu::EvemuDevice::WriteEvent(out->GetStream(), *syn);
}

bool Trimmer::Trim(GenericIStream* in, GenericOStream* out, double from,
                   double to) {
  evemu::EvemuDevice* evemu = replay_->evemu_device();

  input_event event;
  bool trimming = true;

  while (evemu->ReadEvent(in->GetStream(), &event)) {

    // check timestamps only on SYN events.
    if (event.type == EV_SYN) {
      // check if we have reached the from timestamp.
      double timestamp = StimeFromTimeval(&event.time);
      if (timestamp >= from && timestamp < to) {
        if (trimming == true) {
          // turn off trimming and start the output
          // stream by writing the current event state.
          trimming = false;
          replay_->ReplayEvent(event);
          WriteCurrentState(out, &event);
          continue;
        }
      } else if (timestamp >= to) {
        // we have reached the to timestamp. we are done here.
        evemu::EvemuDevice::WriteEvent(out->GetStream(), event);
        break;
      }
    }

    if (trimming) {
      // if we are trimming these events just replay them.
      replay_->ReplayEvent(event);
    } else {
      // write event to output stream
      evemu::EvemuDevice::WriteEvent(out->GetStream(), event);
    }
  }
  return true;
}

}  // namespace replay
