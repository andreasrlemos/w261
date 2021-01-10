#!/usr/bin/env python
"""
This mapper reads from STDIN and waits 0.001 seconds per line.
Its only purpose is to demonstrate one of the scalability ideas.
"""
import sys
import time
for line in sys.stdin:
    time.sleep(0.001)
