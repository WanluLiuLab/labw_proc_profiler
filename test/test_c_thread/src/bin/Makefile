# VERSION=1.0
TARGETS = c_pthread.co c_openmp.co cpp_stdlib.co

SOURCES := $(wildcard *.c *.cpp)
OBJECTS := $(SOURCES:.c=.o)
OBJECTS := $(OBJECTS:.cpp=.o)
LIBTOOL_OBJECTS := $(OBJECTS:.o=.lo)

LDFLAGS += -lcst

all: $(TARGETS)

.PHONY : all

c_openmp.co: c_openmp.lo
	$(LIBTOOL) --tag=CC --mode=link $(LIBTOOL_FLAGS) $(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -fopenmp -o $@ $<

c_pthread.co: c_pthread.lo
	$(LIBTOOL) --tag=CC --mode=link $(LIBTOOL_FLAGS) $(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -lpthread -o $@ $<

cpp_stdlib.co: cpp_stdlib.lo # The backend of C++ thread stdlib is pthread under POSIX systems
	$(LIBTOOL) --tag=CXX --mode=link $(LIBTOOL_FLAGS) $(CXX) $(CXXFLAGS) $(CPPFLAGS) $(LDFLAGS) -lpthread -o $@ $<

c_openmp.lo: c_openmp.c
	$(LIBTOOL) --tag=CC --mode=compile $(LIBTOOL_FLAGS) $(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -fopenmp -c -o $@ $<

%.lo: %.c
	$(LIBTOOL) --tag=CC --mode=compile $(LIBTOOL_FLAGS) $(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -c -o $@ $<

%.lo: %.cpp
	$(LIBTOOL) --tag=CXX --mode=compile $(LIBTOOL_FLAGS) $(CXX) $(CXXFLAGS) $(CPPFLAGS) $(LDFLAGS) -c -o $@ $<

clean:
	$(RM) .libs $(PACKAGE_NAME) $(LIBTOOL_OBJECTS) $(OBJECTS) $(TARGETS)
.PHONY : clean

distclean:
.PHONY : distclean
