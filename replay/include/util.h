// Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef UTIL_H_
#define UTIL_H_

#include <sstream>
#include <string>

namespace replay {

// simple implementation of a lexical cast to convert. Primarily used to
// convert between strings and numeric values.
template<typename T, typename U>
T lexical_cast(U in) {
  std::stringstream ss;
  ss << in;
  T out;
  if (std::string(ss.str()) == std::string("true")) {
    ss.str("1");
  } else if (std::string(ss.str()) == std::string("false")) {
    ss.str("0");
  }
  ss >> out;
  return out;
}

}  // namespace replay

#endif  // UTIL_H_
