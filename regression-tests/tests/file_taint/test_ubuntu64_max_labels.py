# test_ubuntu64_max_labels.py
# Test the file_taint plugin maximum labels option using a 64-bit guest.
#
# Created:  25-OCT-2019

import os

import ptest
import tempfile

import tests.file_taint.common as common

TESTDIR = os.path.dirname(__file__)
REPLAY_PATH = os.path.join("ubuntuserver64", "linux64_positional")

NETDEV = ptest.NetBackend(ptest.NetBackend.USER, "net0")
E1000DEV = ptest.Device(ptest.Device.E1000, backend=NETDEV)

QEMU = ptest.Qemu(ptest.Qemu.X86_64, 2048, NETDEV, E1000DEV)

FILE_TAINT_INPUT1 = ptest.Plugin("file_taint", filename="positional.bin",
    pos=True, max_num_labels=2)

TAINTED_BRANCH = ptest.Plugin("tainted_branch")

# this guest gets its OSI configuration from the default file in osi_linux

_, PLOG1 = tempfile.mkstemp()
REPLAY1 = ptest.Replay(REPLAY_PATH, QEMU, FILE_TAINT_INPUT1, TAINTED_BRANCH,
    os="linux-64-ubuntu:4.4.0-154-generic", plog=PLOG1)

def run():
    retcode = REPLAY1.run()
    if retcode != 0:
        REPLAY1.dump_console(stderr=True)
        return False

    found_branch = False
    found_labels = []
    try:
        with ptest.PlogReader(PLOG1) as plr:
            for i, m in enumerate(plr):
                if m.HasField("tainted_branch"):
                    for tq in m.tainted_branch.taint_query:
                        found_labels += tq.unique_label_set.label
                # block with the cmp for 0x1234
                if m.pc == 0x400878 and m.HasField("tainted_branch"):
                    found_branch = True
                # block with the cmp for 0x2345
                if m.pc == 0x4008A4 and m.HasField("tainted_branch"):
                    print("0x4008A4 should not have been reported")
                    return False
                if m.pc == 0x4008C4 and m.HasField("tainted_branch"):
                    print("0x4008C4 should not have been reported")
                    return False
    except:
        print("error")
    if not found_branch:
        print("expected branch not found")
        return False
    if set(found_labels) != set([0, 1]) or (2 in found_labels or 3 in found_labels):
        print("expected the following labels: {}".format([0, 1]))
        return False

    return True

def cleanup():
    pass