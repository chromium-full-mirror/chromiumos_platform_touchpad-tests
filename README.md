# Touch tests

[TOC]

## Introduction

This repository contains automated tests for [Chromium OS's Gestures library][gestures-lib].
Each test has a log of evdev events which are replayed, a properties file
containing [gesture properties] to set while the Gestures library runs, and a
Python function which verifies the output and returns a test score.

[gestures-lib]: https://chromium.googlesource.com/chromiumos/platform/gestures/+/master/
[gesture properties]: https://chromium.googlesource.com/chromiumos/platform/gestures/+/master/docs/gesture_properties.md

## Setting up

Assuming that you've followed the [developer guide], simply run the following
inside your chroot:

```sh
(inside)
$ cd ~/trunk/src/platform/touchpad-tests
$ sudo make setup-in-place
```

[developer guide]: https://chromium.googlesource.com/chromiumos/platform/gestures/+/master/docs/gesture_properties.md

## Running tests

To run all tests, simply run `touchtests`. To run one or more specific tests,
you can pass a test name or a glob:

```sh
(inside)
$ touchtests atlas-1.0/fat-thumb-fail
$ touchtests atlas-1.0/palm-while-typing*
```

Each test will return a status, with the following meanings:

* **success**: the test succeeded, with the given score out of 1.
* **failure**: the test failed.
* **error**: an error occurred while running the test, so the behavior of the
  gestures library couldn't be evaluated.
* **incomplete**: (baseline tests only) the evdev log for this platform hasn't
  been created.
