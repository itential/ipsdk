# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ipsdk import stringutils

def test_tobool():
    assert stringutils.tobool("true")
    assert stringutils.tobool("yes")
    assert not stringutils.tobool("false")
    assert not stringutils.tobool("no")
    assert not stringutils.tobool(None)
