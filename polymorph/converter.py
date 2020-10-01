# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import ipaddress
from textwrap import wrap
from datetime import datetime, timezone
from dateutil import parser
from polymorph.ftype import Ftype


class Converter(object):
    """This class facilitates the conversion between different data types."""

    def raw2intbe(self, fraw):
        """Convert a set of bytes to Ftype.FT_INT_BE format.
        """
        return int.from_bytes(fraw, byteorder='big')

    def intbe2raw(self, field, fsize):
        """Convert Ftype.FT_INT_BE to a set of bytes.
        """
        return field.to_bytes(fsize, byteorder='big')

    def raw2intle(self, fraw):
        """Convert a set of bytes to Ftype.FT_INT_LE format.
        """
        return int.from_bytes(fraw, byteorder='little')

    def intle2raw(self, field, fsize):
        """Convert Ftype.FT_INT_LE to a set of bytes.
        """
        return field.to_bytes(fsize, byteorder='little')

    def raw2bin(self, fraw, mask, fsize, order='big'):
        """Convert a set of bytes to Ftype.FT_BIN format.
        """
        num_bin = format(int.from_bytes(fraw, byteorder=order),
                         "0" + str(8*fsize) + "b")
        mask_bin = format(mask, "0" + str(8*fsize) + "b")
        trail_zeros = len(mask_bin) - len(mask_bin.rstrip('0'))
        return (int(num_bin, 2) & int(mask_bin, 2)) >> trail_zeros

    def raw2maskbin(self, fraw, prev_mask, fsize, order='big'):
        """Converts a set of bytes to Ftype.FT_BIN format for a field
        whose mask is defined by the previous field."""
        prev_mask_bin = format(prev_mask, "0" + str(8*fsize) + "b")
        inv_mask = int("1"*(8*fsize), 2)
        new_mask = int(prev_mask_bin, 2) ^ inv_mask
        return (self.raw2bin(fraw, new_mask, fsize, order), new_mask)

    def bin2raw(self, field, fraw, mask, fsize, order='big'):
        """Convert Ftype.FT_BIN to a set of bytes.
        """
        mask_bin = format(mask, "0" + str(8*fsize) + "b")
        trail_zeros = len(mask_bin) - len(mask_bin.rstrip('0'))
        field_bin_inv = format(field << trail_zeros, "0" + str(8*fsize) + "b")
        ones = [i for i, item in enumerate(list(mask_bin)) if item == '1']
        old_val = format(int.from_bytes(fraw, byteorder=order),
                         "0" + str(8*fsize) + "b")
        new_val = int(
            old_val[:ones[0]] + field_bin_inv[ones[0]:ones[-1]] + old_val[ones[-1]:], 2)
        return new_val.to_bytes(fsize, byteorder=order)

    def raw2hex(self, fraw):
        """Converts a set of bytes to Ftype.FT_HEX format."""
        return format(int.from_bytes(fraw, byteorder='big'), "#0x")

    def hex2raw(self, field, fsize):
        """Converts Ftype.FT_HEX to a set of bytes."""
        if field[:2] == "0x":
            zeros = fsize * 2 - len(field[2:])
            return bytes.fromhex("0" * zeros + field[2:])
        zeros = fsize * 2 - len(field)
        return bytes.fromhex("0" * zeros + field)

    def raw2string(self, fraw):
        """Converts a set of bytes to Ftype.FT_STRING format."""
        return fraw.decode('utf-8')

    def string2raw(self, field):
        """Converts a Ftype.FT_STRING to a set of bytes."""
        return field.encode('utf-8')

    def raw2ether(self, fraw):
        """Converts a set of bytes to Ftype.FT_BYTES format."""
        return ":".join(wrap(fraw.hex(), 2))

    def ether2raw(self, field):
        """Converts Ftype.FT_BYTES to a set of bytes."""
        return bytes.fromhex(field.replace(":", ""))

    def raw2eui64(self, fraw):
        """Converts a set of bytes to Ftype.FT_EUI64 format."""
        return ":".join(wrap(fraw.hex(), 2)[::-1])

    def eui642raw(self, field):
        """Converts Ftype.FT_EUI64 format to a set of bytes."""
        return bytes.fromhex("".join(field.split(":")[::-1]))

    def raw2ipv4(self, fraw):
        """Converts a set of bytes to Ftype.FT_IPV4 format."""
        if len(fraw) == 4:
            return str(ipaddress.IPv4Address(fraw))

    def ipv42raw(self, field):
        """Converts Ftype.FT_IPV4 to a set of bytes."""
        return ipaddress.IPv4Address(field).packed

    def raw2ipv6(self, fraw):
        """Converts a set of bytes to Ftype.FT_IPV4 format."""
        if len(fraw) == 16:
            return str(ipaddress.IPv6Address(fraw))

    def ipv62raw(self, field):
        """Converts Ftype.FT_IPV4 to a set of bytes."""
        return ipaddress.IPv6Address(field).packed

    def raw2absolute(self, fraw, fsize, fname):
        """Converts a set of bytes to Ftype.FT_ABSOLUTE_TIME format."""
        if fsize == 4:
            return datetime.fromtimestamp(
                int(fraw.hex(), 16)).strftime("%b %e, %Y %H:%M:%S.%f")
        elif fsize == 8:
            if "ntp." in fname:
                return datetime.fromtimestamp(
                    int(fraw.hex()[:8], 16) - 2208988800,
                    tz=timezone.utc).strftime("%b %e, %Y %H:%M:%S.%f")
            else:
                return datetime.fromtimestamp(
                    int.from_bytes(fraw, 'little')).strftime("%b %e, %Y %H:%M:%S.%f")

    def absolute2raw(self, field, fraw, fsize, fname):
        """Convert Ftype.FT_ABSOLUTE_TIME to a set of bytes."""
        if fsize == 4:
            dt = parser.parse(field).timestamp()
            return int(dt).to_bytes(fsize, 'big')
        elif fsize == 8:
            if "ntp." in fname:
                dt = int(parser.parse(field + " UTC").timestamp() + 2208988800)
                return dt.to_bytes(4, 'big') + fraw[4:]
            else:
                dt = parser.parse(field).timestamp()
                return int(dt).to_bytes(fsize, 'little')

    def raw2relative(self, fraw):
        """Converts a set of bytes to Ftype.FT_RELATIVE_TIME format."""
        time = format(int.from_bytes(fraw, 'big'), "<016")
        return time[:7] + "." + time[7:]

    def relative2raw(self, field, fsize):
        """Converts Ftype.FT_RELATIVE_TIME to a set of bytes."""
        return int(field.replace(".", "").strip('0')).to_bytes(fsize, 'big')

    def get_frepr(self, ftype, fraw, fsize, fmask, fname):
        """Returns the representation of a field from its value in bytes."""
        if ftype in [Ftype.FT_INT_BE]:
            return self.raw2intbe(fraw)
        elif ftype in [Ftype.FT_INT_LE]:
            return self.raw2intle(fraw)
        elif ftype in [Ftype.FT_STRING]:
            return self.raw2string(fraw)
        elif ftype in [Ftype.FT_BYTES]:
            return fraw
        elif ftype in [Ftype.FT_BIN_BE]:
            return self.raw2bin(fraw, fmask, fsize, order='big')
        elif ftype in [Ftype.FT_BIN_LE]:
            return self.raw2bin(fraw, fmask, fsize, order='little')
        elif ftype in [Ftype.FT_HEX]:
            return self.raw2hex(fraw)
        elif ftype in [Ftype.FT_ETHER]:
            return self.raw2ether(fraw)
        elif ftype in [Ftype.FT_IPv4]:
            return self.raw2ipv4(fraw)
        elif ftype in [Ftype.FT_IPv6]:
            return self.raw2ipv6(fraw)
        elif ftype in [Ftype.FT_ABSOLUTE_TIME]:
            return self.raw2absolute(fraw, fsize, fname)
        elif ftype in [Ftype.FT_RELATIVE_TIME]:
            return self.raw2relative(fraw)
        elif ftype in [Ftype.FT_EUI64]:
            return self.raw2eui64(fraw)

    def get_fraw(self, field, ftype, fraw, fsize, fmask, fname):
        """Returns the field value in bytes from its representation."""
        if ftype in [Ftype.FT_INT_BE]:
            return self.intbe2raw(field, fsize)
        elif ftype in [Ftype.FT_INT_LE]:
            return self.intle2raw(field, fsize)
        elif ftype in [Ftype.FT_STRING]:
            return self.string2raw(field)
        elif ftype in [Ftype.FT_BYTES]:
            return field
        elif ftype in [Ftype.FT_BIN_BE]:
            return self.bin2raw(field, fraw, fmask, fsize, order='big')
        elif ftype in [Ftype.FT_BIN_LE]:
            return self.bin2raw(field, fraw, fmask, fsize, order='little')
        elif ftype in [Ftype.FT_HEX]:
            return self.hex2raw(field, fsize)
        elif ftype in [Ftype.FT_ETHER]:
            return self.ether2raw(field)
        elif ftype in [Ftype.FT_IPv4]:
            return self.ipv42raw(field)
        elif ftype in [Ftype.FT_IPv6]:
            return self.ipv62raw(field)
        elif ftype in [Ftype.FT_ABSOLUTE_TIME]:
            return self.absolute2raw(field, fraw, fsize, fname)
        elif ftype in [Ftype.FT_RELATIVE_TIME]:
            return self.relative2raw(field, fsize)
        elif ftype in [Ftype.FT_EUI64]:
            return self.eui642raw(field)
