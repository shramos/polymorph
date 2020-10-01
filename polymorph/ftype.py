# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from enum import Enum


class Ttype(Enum):
    """Enum of types used by Tshark for network packet fields."""
    FT_HEX = -1
    FT_NONE = 0
    FT_PROTOCOL = 1
    FT_BOOLEAN = 2
    FT_CHAR = 3
    FT_UINT8 = 4
    FT_UINT16 = 5
    FT_UINT24 = 6
    FT_UINT32 = 7
    FT_UINT40 = 8
    FT_UINT48 = 9
    FT_UINT56 = 10
    FT_UINT64 = 11
    FT_INT8 = 12
    FT_INT16 = 13
    FT_INT24 = 14
    FT_INT32 = 15
    FT_INT40 = 16
    FT_INT48 = 17
    FT_INT56 = 18
    FT_INT64 = 19
    FT_IEEE_11073_SFLOAT = 20
    FT_IEEE_11073_FLOAT = 21
    FT_FLOAT = 22
    FT_DOUBLE = 23
    FT_ABSOLUTE_TIME = 24
    FT_RELATIVE_TIME = 25
    FT_STRING = 26
    FT_STRINGZ = 27
    FT_UINT_STRING = 28
    FT_ETHER = 29
    FT_BYTES = 30
    FT_UINT_BYTES = 31
    FT_IPv4 = 32
    FT_IPv6 = 33
    FT_IPXNET = 34
    FT_FRAMENUM = 35
    FT_PCRE = 36
    FT_GUID = 37
    FT_OID = 38
    FT_EUI64 = 39
    FT_AX25 = 40
    FT_VINES = 41
    FT_REL_OID = 42
    FT_SYSTEM_ID = 43
    FT_STRINGZPAD = 44
    FT_FCWWN = 45
    FT_NUM_TYPES = 46


class Ftype(Enum):
    """Enum of types used by Polymorph for network packet fields."""
    FT_INT_BE = 0  # Int big endian
    FT_INT_LE = 1  # Int little endian
    FT_STRING = 2
    FT_BYTES = 3
    FT_BIN_BE = 4
    FT_BIN_LE = 5
    FT_HEX = 6
    FT_ETHER = 7
    FT_IPv4 = 8
    FT_IPv6 = 9
    FT_ABSOLUTE_TIME = 10
    FT_RELATIVE_TIME = 11
    FT_EUI64 = 12
