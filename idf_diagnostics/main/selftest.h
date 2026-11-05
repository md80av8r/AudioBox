// Board self-test: writes a plain-text report. Returns the number of failed checks.
#pragma once
#include <stddef.h>

int selftest_run(char *buf, size_t size, int *passed);
