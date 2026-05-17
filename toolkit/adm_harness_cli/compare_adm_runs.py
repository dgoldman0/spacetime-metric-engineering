#!/usr/bin/env python3
from adm_harness.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["compare", *(__import__("sys").argv[1:])]))
