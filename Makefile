# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DESTDIR ?= target
LOCALDESTDIR=$(shell readlink -f local-install)
OVERLAY=../../third_party/chromiumos-overlay/

export DESTDIR

ifeq ($(origin SYSROOT), undefined)
	XORG_CONF_DIR=../xorg-conf
else
	XORG_CONF_DIR=$(CROS_WORKON_SRCROOT)/src/platform/xorg-conf
endif

all: framework

clean:
	$(MAKE) -C framework clean

framework:
	$(MAKE) -C framework all

tests:
	$(MAKE) -C framework tests

install:
	mkdir -p $(DESTDIR)
	$(MAKE) -C framework install

	install -D touchtests $(DESTDIR)/touchtests

	# for each filetype in tests folder
	for extension in dat props log py ; do \
		find tests \( -iname \*.$$extension ! -wholename \*/.\* ! -wholename \
				\*/:\* \) -exec install -D -m 0755 \{\} $(DESTDIR)/\{\} \; ; \
	done

	mkdir -p $(DESTDIR)/xorg-conf/
	for xorgfile in $(XORG_CONF_DIR)/* ; do \
		install -D $$xorgfile \
			$(DESTDIR)/xorg-conf/$(shell basename $$xorgfile); \
	done

setup-in-place:
	OUT=. $(MAKE) -C ../mttools setup-in-place

	# Create local-install folder with links to
	# original folders. So there is no need to reinstall after changes.
	install -D touchtests $(LOCALDESTDIR)/touchtests

	ln -sfn $(shell readlink -f $(XORG_CONF_DIR)) local-install/xorg-conf-files
	ln -sfn ../framework/src local-install/framework
	ln -sfn ../tests local-install/tests
	ln -sf $(LOCALDESTDIR)/touchtests /usr/bin/touchtests

in-place:
	OUT=. $(MAKE) -C ../mttools in-place

clean-in-place:
	OUT=. $(MAKE) -C ../mttools clean-in-place

.PHONY: all clean framework tests install local-install
