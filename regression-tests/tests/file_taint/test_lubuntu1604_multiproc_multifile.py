import os

import ptest
import tempfile

import tests.file_taint.common as common

TESTDIR = os.path.dirname(__file__)

NETDEV = ptest.NetBackend(ptest.NetBackend.USER, "net0")
RTL8139 = ptest.Device(ptest.Device.RTL8139, backend=NETDEV)

QEMU = ptest.Qemu(ptest.Qemu.I386, 2048, NETDEV, RTL8139, vga=ptest.Qemu.CIRRUS)

FILE_TAINT_INPUT1 = ptest.Plugin("file_taint", filename="input1.bin")
FILE_TAINT_INPUT2 = ptest.Plugin("file_taint", filename="input2.bin")
FILE_TAINT_INPUT3 = ptest.Plugin("file_taint", filename="should-not-be-tainted")

TAINTED_BRANCH = ptest.Plugin("tainted_branch")

OSI = ptest.Plugin("osi")
OSI_LINUX = ptest.Plugin("osi_linux", kconf_file=os.path.join("shared_configs",
    "lubuntu_kernelinfo.conf"))

_, PLOG1 = tempfile.mkstemp()
REPLAY1 = ptest.Replay("lubuntu1604-filetaint-multiproc-multifile", QEMU,
    OSI, OSI_LINUX, FILE_TAINT_INPUT1, TAINTED_BRANCH, os="linux-32-ubuntu-4.4.0-21-generic", plog=PLOG1)
_, PLOG2 = tempfile.mkstemp()
REPLAY2 = ptest.Replay("lubuntu1604-filetaint-multiproc-multifile", QEMU,
    OSI, OSI_LINUX, FILE_TAINT_INPUT2, TAINTED_BRANCH, os="linux-32-ubuntu-4.4.0-21-generic", plog=PLOG2)
_, PLOG3 = tempfile.mkstemp()
REPLAY3 = ptest.Replay("lubuntu1604-filetaint-multiproc-multifile", QEMU,
    OSI, OSI_LINUX, FILE_TAINT_INPUT3, TAINTED_BRANCH, os="linux-32-ubuntu-4.4.0-21-generic", plog=PLOG2)

def run():
    # Try the first process
    retcode = REPLAY1.run()
    if retcode != 0:
        REPLAY1.dump_console(stdout=True, stderr=True)
        return False

    if not common.linux_checkplog(PLOG1):
        return False

    # Try the second process
    retcode = REPLAY2.run()
    if retcode != 0:
        REPLAY2.dump_console(stdout=True, stderr=True)
        return False
    if not common.linux_checkplog(PLOG2):
        return False

    # Try to taint a file that we didn't open. The plog file should be empty.
    retcode = REPLAY3.run()
    if retcode != 0:
        REPLAY3.dump_console(stdout=True, stderr=True)
        return False
    try:
        common.linux_checkplog(PLOG3)
        return False
    except:
        pass

    return True

def cleanup():
    pass