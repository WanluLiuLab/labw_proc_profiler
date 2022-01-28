
export PROJECT_NAME := proc_profiler

include .maint/makefiles/common_environment.mk
include .maint/makefiles/general_pub.mk
include .maint/makefiles/python_test.mk
include .maint/makefiles/python_pub.mk
include .maint/makefiles/doc_adapter.mk

clean:
	$(RM) .pytest_cache
	$(MAKE) -C test/simple_multithread clean

distclean: clean
	$(RM) activate.sh renv.lock .Rprofile renv venv

test_profiler:
	$(MAKE) -C test/simple_multithread
	bin/proc_profiler.sh test/simple_multithread/simple_multithread
