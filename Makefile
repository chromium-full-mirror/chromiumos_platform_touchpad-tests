# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DESTDIR ?= target
LOCALDESTDIR=$(shell readlink -f local-install)
OVERLAY=../../third_party/chromiumos-overlay/
XORG_CONF_DIR=../xorg-conf

all: framework

clean:
	make -C framework clean

framework:
	make -C framework all

tests:
	make -C framework tests

install:
	mkdir -p $(DESTDIR)
	DESTDIR=$(shell readlink -f $(DESTDIR)) make -C framework install

	install -D touchtests $(DESTDIR)/touchtests

	# for each filetype in tests folder
	for extension in dat props log py ; do \
		find tests \( -iname \*.$$extension ! -wholename \*/.\* ! -wholename \
				\*/:\* \) -exec install -D -m 0755 \{\} $(DESTDIR)/\{\} \; ; \
	done

	mkdir -p $(DESTDIR)/xorg-conf-files/
	for xorgfile in $(XORG_CONF_DIR)/* ; do \
		install -D $$xorgfile \
			$(DESTDIR)/xorg-conf-files/$(shell basename $$xorgfile); \
	done

setup-in-place:
	OUT=. make -C ../mttools setup-in-place

	# Create local-install folder with links to
	# original folders. So there is no need to reinstall after changes.
	install -D touchtests $(LOCALDESTDIR)/touchtests

	ln -sfn $(shell readlink -f $(XORG_CONF_DIR)) local-install/xorg-conf-files
	ln -sfn ../framework/src local-install/framework
	ln -sfn ../tests local-install/tests
	ln -sf $(LOCALDESTDIR)/touchtests /usr/bin/touchtests

in-place:
	OUT=. make -C ../mttools in-place

clean-in-place:
	OUT=. make -C ../mttools clean-in-place

.PHONY: all clean framework tests install local-install
