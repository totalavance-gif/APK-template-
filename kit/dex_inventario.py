#!/usr/bin/env python3
"""Inventario liviano de clases por dex (solo stdlib).

Lee UN dex a la vez y lista sus class_defs con superclase y total de
metodos declarados. RAM usada: ~tamano de un dex (unos MB), nunca el APK
completo ni todos los dex a la vez.

Uso:
    dex_inventario.py classesN.dex [-o salida.txt] [-q]
"""
import struct
import sys


def uleb128(buf, off):
    val = shift = 0
    while True:
        b = buf[off]
        off += 1
        val |= (b & 0x7F) << shift
        if not b & 0x80:
            return val, off
        shift += 7


def get_string(buf, string_ids_off, idx):
    (str_off,) = struct.unpack_from("<I", buf, string_ids_off + idx * 4)
    _, p = uleb128(buf, str_off)
    end = buf.index(b"\x00", p)
    return bytes(buf[p:end]).decode("utf-8", "replace")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__.strip().splitlines()[-3])
        return 2
    path = args[0]
    out_path = None
    if "-o" in sys.argv:
        out_path = sys.argv[sys.argv.index("-o") + 1]
    quiet = "-q" in sys.argv

    with open(path, "rb") as f:
        buf = f.read()
    if buf[:4] != b"dex\n":
        print(f"ERROR: {path} no es un dex", file=sys.stderr)
        return 1

    (string_ids_size,) = struct.unpack_from("<I", buf, 0x38)
    (string_ids_off,) = struct.unpack_from("<I", buf, 0x3C)
    (type_ids_size,) = struct.unpack_from("<I", buf, 0x40)
    (type_ids_off,) = struct.unpack_from("<I", buf, 0x44)
    (method_ids_size,) = struct.unpack_from("<I", buf, 0x58)
    (class_defs_size,) = struct.unpack_from("<I", buf, 0x60)
    (class_defs_off,) = struct.unpack_from("<I", buf, 0x64)

    def typename(tidx):
        if tidx == 0xFFFFFFFF:
            return "-"
        (sidx,) = struct.unpack_from("<I", buf, type_ids_off + tidx * 4)
        return get_string(buf, string_ids_off, sidx)

    lines = []
    for i in range(class_defs_size):
        base = class_defs_off + i * 32
        (cidx, _, sidx, _, src_idx, _, class_data_off, _) = struct.unpack_from(
            "<8I", buf, base
        )
        n_methods = 0
        if class_data_off:
            p = class_data_off
            _, p = uleb128(buf, p)  # static fields
            _, p = uleb128(buf, p)  # instance fields
            n_direct, p = uleb128(buf, p)
            n_virtual, p = uleb128(buf, p)
            n_methods = n_direct + n_virtual
        src = (
            get_string(buf, string_ids_off, src_idx)
            if src_idx != 0xFFFFFFFF
            else "-"
        )
        lines.append(f"{typename(cidx)}\tsuper={typename(sidx)}"
                     f"\tmethods={n_methods}\tsrc={src}")

    if out_path:
        with open(out_path, "w") as f:
            f.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))
    if not quiet:
        print(f"# {path}: {class_defs_size} clases, "
              f"{type_ids_size} tipos, {method_ids_size} metodos, "
              f"{string_ids_size} strings", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
