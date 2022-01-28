LIBTARGETS = cst
TARGETS := $(foreach fn, $(LIBTARGETS), $(addprefix lib, $(fn)))
TARGETS := $(foreach fn, $(TARGETS), $(addsuffix .so, $(fn)))
TARGETS_LA := $(TARGETS:so=la)

SOURCES := $(wildcard *.c *.cpp)
OBJECTS := $(SOURCES:.c=.o)
OBJECTS := $(OBJECTS:.cpp=.o)
LIBTOOL_OBJECTS := $(OBJECTS:.o=.lo)

CFLAGS := $(CFLAGS) --shared
CPPFLAGS := $(CPPFLAGS) --shared

all: $(TARGETS)

%.so: %.la
	$(LIBTOOL) --tag=CC --mode=link $(LIBTOOL_FLAGS) $(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

libcst.la: cst_workload.lo
	$(LIBTOOL) --tag=CC --mode=link $(LIBTOOL_FLAGS) $(CC) $(CFLAGS) $(LDFLAGS) -lm -o $@ $^

%.lo: %.c
	$(LIBTOOL) --tag=CC --mode=compile  $(LIBTOOL_FLAGS) $(CC) $(CFLAGS) $(CPPFLAGS) $< -c -o $@

%.lo: %.cpp
	$(LIBTOOL) --tag=CXX --mode=compile  $(LIBTOOL_FLAGS) $(CXX) $(CPPFLAGS) $(CPPFLAGS) $< -c -o $@ \

clean:
	$(RM) .libs $(PACKAGE_NAME) $(LIBTOOL_OBJECTS) $(OBJECTS) $(TARGETS) $(TARGETS_LA)
.PHONY: clean

distclean:
.PHONY: distclean
