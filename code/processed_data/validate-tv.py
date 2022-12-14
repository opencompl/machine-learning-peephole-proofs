#!/usr/bin/env python3
import argparse
import os
import glob
import subprocess
from pathlib import Path
import csv
import asyncio
import itertools

# Script that validates translation validation programs and
# generates a CSV of the results, and stores the valid program
# pairs in a separate folder.

PARSER = argparse.ArgumentParser(prog = 'ValidateTV', description = 'Validates alive files in a given folder, and saves the correct ones to a different folder')
PARSER.add_argument('inputdir', help="input directory of all TV files. default: '/tmp/instcombine'")         
PARSER.add_argument('outputdir', help="output directory where valid files are stored. default: '/tmp/instcombine-correct'")        
PARSER.add_argument('logpath', help="path to CSV log file. default: './log.csv'")        

async def main():
    args = PARSER.parse_args()
    processes = []
    # programs = []
    filepaths = list(glob.glob(str(Path(args.inputdir) / "*.ll" )))
    for (i, filepath) in enumerate(filepaths):
        print("running: %40s | %6.2f %%" % (filepath, i / len(filepaths) * 100.0))
        proc = await asyncio.create_subprocess_exec("alive-tv", filepath, "--quiet", \
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        processes.append(proc.communicate())
    processes = await asyncio.gather(*processes)

    # status = success, failure, timeout
    rows = []
    header = ["filepath", "status", "output"]
    for (filepath, proc) in zip(filepaths, processes):
        (stdout, stderr) = proc #await proc.communicate()
        if b"Timeout" in stdout: status = "timeout"
        elif b"ERROR" in stdout: status = "error"
        else: status = "success"
        rows.append([filepath, status, stdout])
        with open(args.logpath, "w") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

if __name__ == "__main__":
    asyncio.run(main())
