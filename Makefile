# Makefile for Win-NetSight (Windows Only)

# C++ Compiler for MSVC (Visual Studio)
MSVC_CXX = cl.exe
MSVC_LIBS = iphlpapi.lib ws2_32.lib
MSVC_FLAGS = /EHsc /O2

# C++ Compiler for MinGW (GCC on Windows)
MINGW_CXX = g++
MINGW_LIBS = -lws2_32 -liphlpapi
MINGW_FLAGS = -O2 -std=c++17

TARGET_CORE = netsight_core.exe

.PHONY: all msvc mingw clean

all: msvc

# Build with MSVC
msvc: $(TARGET_CORE)
	$(MSVC_CXX) $(MSVC_FLAGS) netsight_core.cpp /link $(MSVC_LIBS) /out:$(TARGET_CORE)

# Build with MinGW
mingw: $(TARGET_CORE)
	$(MINGW_CXX) $(MINGW_FLAGS) netsight_core.cpp -o $(TARGET_CORE) $(MINGW_LIBS)

clean:
	@echo Cleaning up...
	-del $(TARGET_CORE) 2>NUL || true
	-rm $(TARGET_CORE) 2>NUL || true
