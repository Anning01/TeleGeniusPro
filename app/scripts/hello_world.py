#!/usr/bin/env python
import argparse
import sys


class Mian:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Hello World Script')
        parser.add_argument('--name', type=str, default='World', help='Name to greet')
        parser.add_argument('--pass', type=str, default='World', help='Name to greet')
        self.args = parser.parse_args()

    def main(self):
        print(self.args)

        print(f"Hello, {self.args}!")
        return 0

if __name__ == "__main__":
    sys.exit(Mian().main())