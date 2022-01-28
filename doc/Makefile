#!/usr/bin/env make
#===============================================================================
# Copyright (C) 2021-2022. tetgs authors
#
# This file is a part of tetgs, which is licensed under MIT,
# a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
# NAME: Makefile -- Makefile of building sphinx documentations
#
# VERSION HISTORY:
# 2021-08-20 0.1  : Purposed and added by YU Zhejian.
#
#===============================================================================

SPHINX_OPTS := -j auto

SPHINX_APIDOC_ARGS := --separate \
	--no-toc \
	--module-first \
	--maxdepth 2 \
	--force \
	--output-dir $(CURDIR)/_apidoc \
	--doc-project 'API Docs'

BUILD_DIR := $(CURDIR)/_build

.PHONY: all

all: pdf html

activate.sh: activate.sh.in
	bash $(CURDIR)/setup.sh

.PHONY: apidoc
apidoc: activate.sh
	BASH_ENV=$(CURDIR)/activate.sh bash -c "sphinx-apidoc $(SPHINX_APIDOC_ARGS) $(PWD)/src/proc_profiler"
	BASH_ENV=$(CURDIR)/activate.sh bash -c "sphinx-apidoc $(SPHINX_APIDOC_ARGS) $(PWD)/src/pid_monitor"

html: activate.sh apidoc
	BASH_ENV=$(CURDIR)/activate.sh bash -c "sphinx-build -M html $(CURDIR) $(BUILD_DIR) $(SPHINX_OPTS)"

pdf: activate.sh apidoc
	BASH_ENV=$(CURDIR)/activate.sh bash -c "sphinx-build -M latexpdf $(CURDIR) $(BUILD_DIR) $(SPHINX_OPTS)"

clean:
	$(RM) $(BUILD_DIR)

distclean:
