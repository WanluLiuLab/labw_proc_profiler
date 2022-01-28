# VERSION=1.5
TARGETS := lib bin
export VPATH += $(CURDIR)/bin/ $(CURDIR)/lib/ $(CURDIR)/include/
export CPPFLAGS += -I$(CURDIR)/include
export CFLAGS += -Wall -Wextra --std=c99
export CXXFLAGS += -Wall -Wextra --std=c++11
export LDFLAGS += -L$(CURDIR)/lib
export LIBTOOL := libtool
export RM := rm -rf

all: $(TARGETS)

lib:
	@$(MAKE) -C $(CURDIR)/lib/
.PHONY: lib

bin: lib
	@$(MAKE) -C $(CURDIR)/bin/
.PHONY: bin

clean:
	@$(MAKE) -C $(CURDIR)/lib clean
	@$(MAKE) -C $(CURDIR)/bin clean
	$(RM) .libs $(PACKAGE_NAME)
.PHONY: clean

distclean: clean
	@$(MAKE) -C $(CURDIR)/bin distclean
	@$(MAKE) -C $(CURDIR)/lib distclean
.PHONY: distclean

assess: # Used for developmental purpose only.
	scan-build -o scan-build make clean all RM="rm -rf" LIBTOOL=libtool CP="echo"
	cppcheck --library=zlib --library=posix -I include --platform=unix64  bin include lib
.PHONY: assess

