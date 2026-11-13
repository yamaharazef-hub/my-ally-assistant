# -*- coding: utf-8 -*-
"""Minimal reader/writer for Steam's binary `shortcuts.vdf`.

Format ( KeyValues binary, little endian ):

    0x00 "shortcuts" 0x00
      per entry:
        0x00 "<index>" 0x00
          0x02 "appid" 0x00            <uint32 LE>
          0x01 "AppName" 0x00          <c-string>
          ... known string/int fields ...
          0x00 "tags" 0x00 (0x01 "<i>" 0x00 "<tag>" 0x00)* 0x08
        0x08
    0x08 0x08

We deliberately keep every field we read (including unknown ones) so
rewriting the file is lossless for entries we do not touch.
"""

import struct

T_OBJECT = 0x00
T_STRING = 0x01
T_INT32 = 0x02
T_END = 0x08


class VDFError(Exception):
    pass


def _read_cstring(data, pos):
    end = data.index(b"\x00", pos)
    return data[pos:end].decode("utf-8", "replace"), end + 1


def _read_entry(data, pos):
    """Read one shortcut object after its 0x00 tag. Returns (dict, newpos)."""
    name, pos = _read_cstring(data, pos)   # entry index; preserved verbatim
    entry = {"_index": name, "tags": []}
    while True:
        if pos >= len(data):
            raise VDFError("unexpected end of shortcuts.vdf")
        ftype = data[pos]
        pos += 1
        if ftype == T_END:
            break
        key, pos = _read_cstring(data, pos)
        if ftype == T_STRING:
            value, pos = _read_cstring(data, pos)
            if key == "tags" or key == "_index":
                pass
            else:
                entry[key] = value
        elif ftype == T_INT32:
            entry[key] = struct.unpack_from("<i", data, pos)[0]
            pos += 4
        elif ftype == T_OBJECT:
            if key == "tags":
                # tags object: 0x01 "<i>" 0x00 "<tag>" 0x00 ... 0x08
                while data[pos] != T_END:
                    if data[pos] != T_STRING:
                        raise VDFError("unexpected tag field type")
                    pos += 1
                    _, pos = _read_cstring(data, pos)      # index
                    tag, pos = _read_cstring(data, pos)    # value
                    entry["tags"].append(tag)
                pos += 1   # T_END of tags
            else:
                raise VDFError(f"unknown nested object '{key}'")
        else:
            raise VDFError(f"unknown field type {ftype:#x}")
    return entry, pos


def load_shortcuts(path):
    """Parse shortcuts.vdf -> ordered list of entry dicts (newest last)."""
    with open(path, "rb") as fh:
        return load_shortcuts_from_bytes(fh.read())


def load_shortcuts_from_bytes(data):
    """Parse raw shortcuts.vdf bytes -> ordered list of entry dicts."""
    entries = []
    if not data:
        return entries
    if data[0] != T_OBJECT:
        raise VDFError("not a shortcuts.vdf file")
    magic, pos = _read_cstring(data, 1)
    if magic != "shortcuts":
        raise VDFError("not a shortcuts.vdf file")

    while pos < len(data):
        ftype = data[pos]
        pos += 1
        if ftype == T_END:
            break
        if ftype != T_OBJECT:
            raise VDFError(f"unexpected byte {ftype:#x} at {pos}")
        entry, pos = _read_entry(data, pos)
        entries.append(entry)

    # tolerate the trailing 0x08
    if pos < len(data) and data[pos] == T_END:
        pos += 1
    return entries


def dump_shortcuts(entries):
    """Serialise entry dicts back to the binary shortcuts.vdf layout."""
    buf = bytearray()
    buf += bytes([T_OBJECT]) + b"shortcuts\x00"
    for idx, entry in enumerate(entries):
        buf += bytes([T_OBJECT]) + str(idx).encode() + b"\x00"
        for key, value in entry.items():
            if key in ("_index", "tags"):
                continue
            if isinstance(value, int):
                buf += bytes([T_INT32]) + key.encode() + b"\x00"
                buf += struct.pack("<i", value)
            else:
                buf += bytes([T_STRING]) + key.encode() + b"\x00"
                buf += str(value).encode("utf-8") + b"\x00"
        # tags object
        buf += bytes([T_OBJECT]) + b"tags\x00"
        for i, tag in enumerate(entry.get("tags", [])):
            buf += bytes([T_STRING]) + str(i).encode() + b"\x00"
            buf += str(tag).encode("utf-8") + b"\x00"
        buf += bytes([T_END])
        buf += bytes([T_END])      # end of entry object
    buf += bytes([T_END, T_END])   # end of 'shortcuts', end of file
    return bytes(buf)


def save_shortcuts(path, entries):
    """Write entries to path (caller is responsible for backups)."""
    with open(path, "wb") as fh:
        fh.write(dump_shortcuts(entries))
