#!/usr/bin/env python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Hello World Script')
    parser.add_argument('--name', type=str, default='World', help='Name to greet')
    args = parser.parse_args()
    
    print(f"Hello, {args.name}!")
    return 0

if __name__ == "__main__":
    sys.exit(main())