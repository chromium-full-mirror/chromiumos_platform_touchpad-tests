# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

DESTDIR ?= target
LOCALDESTDIR=$(shell readlink -f local-install)

all: replay framework

clean:
	OUT=build make -C replay clean
	make -C framework clean

replay:
	OUT=build make -C replay all

framework:
	make -C framework all

tests:
	OUT=build make -C replay tests
	make -C framework tests

install:
	mkdir -p $(DESTDIR)
	DESTDIR=$(shell readlink -f $(DESTDIR)) OUT=build make -C replay install
	DESTDIR=$(shell readlink -f $(DESTDIR)) make -C framework install

	install -D touchtests $(DESTDIR)/touchtests

	# for each filetype in tests folder
	# install all files of this type. Ignore paths with . or : in them

	for extension in dat props log py ; do \
		find tests \( -iname \*.$$extension ! -wholename \*/.\* ! -wholename \
				\*/:\* \) -exec install -D -m 0755 \{\} $(DESTDIR)/\{\} \; ; \
	done

local-install:
	# install script locally. Create local-install folder with links to
	# original folders. So there is no need to reinstall after changes.
	install -D touchtests $(LOCALDESTDIR)/touchtests

	ln -sf ../framework/src local-install/framework
	ln -sf ../replay/build/replay local-install/replay
	ln -sf ../tests local-install/tests
	ln -sf $(LOCALDESTDIR)/touchtests /usr/bin/touchtests

.PHONY: all clean replay framework tests install local-install