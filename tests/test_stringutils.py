# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ipsdk import stringutils

def test_string_to_bool_cases():
    assert stringutils.string_to_bool("true")
    assert stringutils.string_to_bool("yes")
    assert not stringutils.string_to_bool("false")
    assert not stringutils.string_to_bool("no")
    assert not stringutils.string_to_bool(None)


