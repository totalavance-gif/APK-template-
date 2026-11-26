#!/usr/bin/env python3
"""Kit 2 parches sobre YouTube stock 21.47.483-BETA (1561317017).

Dos fases (ver build.yml):
  aplicar.py smali <dir_decodificado> <dir_kit>  # enganches smali
  aplicar.py dex   <apk_construida>   <dir_kit>  # inyecta extension.dex

Idempotente y solo stdlib. Aborta si las huellas no cuadran.
"""
import glob
import os
import shutil
import sys
import tempfile
import zipfile

HOOK_T = """    invoke-static/range {p1 .. p1}, Lacvk;->patch_filterVideoAdTriggers(Ljava/util/List;)Ljava/util/List;

    move-result-object p1

    invoke-static {}, Lapp/morphe/extension/youtube/patches/ads/AdsPatch;->hideVideoAds()Z

    move-result v0

    if-eqz v0, :cond_b

    return-void

    :cond_b
    nop

"""

BG_V0 = """    invoke-static {v0}, Lapp/morphe/extension/youtube/patches/misc/BackgroundPlaybackPatch;->isBackgroundPlaybackAllowed(Z)Z

    move-result v0

    return v0"""


def find_smali(root, name):
    hits = glob.glob(os.path.join(root, "smali*", name))
    if not hits:
        raise SystemExit(f"ERROR: no se encontro {name} en {root}/smali*")
    return hits[0]


def buscar(src, aguja, donde, inicio=0):
    try:
        return src.index(aguja, inicio)
    except ValueError:
        raise SystemExit(f"ERROR: huella no encontrada en {donde}: {aguja!r} "
                         f"(base distinta a 1561317017?)")


def parche_ads(root, kit):
    p = find_smali(root, "acvk.smali")
    src = open(p).read()
    if "patch_filterVideoAdTriggers(Ljava/util/List;)Ljava/util/List;" in src:
        print("ads: metodo patch_* ya existe, skip")
    else:
        metodo = open(os.path.join(kit, "metodo_ads.smali")).read()
        if not src.endswith("\n"):
            src += "\n"
        src = src + "\n" + metodo
        print("ads: metodo patch_* anadido")
    ini = buscar(src, ".method public final t(Ljava/util/List;)V", "acvk")
    fin = buscar(src, ".end method", "acvk.t", ini)
    cuerpo_t = src[ini:fin]
    if "patch_filterVideoAdTriggers" in cuerpo_t:
        print("ads: enganche en t() ya existe, skip")
    else:
        ancla = "    move-object/from16 v1, p0\n"
        if ancla not in cuerpo_t:
            raise SystemExit("ERROR: huella de acvk.t() no encontrada")
        idx = cuerpo_t.index(ancla)
        siguiente = cuerpo_t[idx + len(ancla):idx + len(ancla) + 200]
        if "new-instance v2, Landroid/util/SparseArray;" not in siguiente:
            raise SystemExit("ERROR: huella incompleta en acvk.t()")
        cuerpo_t = cuerpo_t[:idx] + HOOK_T + cuerpo_t[idx:]
        src = src[:ini] + cuerpo_t + src[fin:]
        print("ads: enganche en t() insertado")
    open(p, "w").write(src)


def parche_bg(root):
    p = find_smali(root, "argv.smali")
    src = open(p).read()
    if "isBackgroundPlaybackAllowed" in src:
        print("bg: enganche ya existe, skip")
        return
    ini = buscar(src, ".method public static B(Lbhsd;)Z", "argv")
    fin = buscar(src, ".end method", "argv.B", ini)
    cuerpo = src[ini:fin]
    # huella de mapeo: el gate boolean del original
    if "Lbdow;->c:Z" not in cuerpo:
        raise SystemExit("ERROR: huella de mapeo en argv.B() "
                         "(base distinta a 1561317017?)")
    pos = cuerpo.rfind("    return v0\n")
    if pos < 0:
        raise SystemExit("ERROR: return de argv.B() no encontrado")
    cuerpo = cuerpo[:pos] + BG_V0 + "\n" + cuerpo[pos + len("    return v0\n"):]
    src = src[:ini] + cuerpo + src[fin:]
    print("bg: return de B() envuelto")
    open(p, "w").write(src)


def inyectar_dex(apk, kit):
    ext = os.path.join(kit, "extension.dex")
    if not os.path.exists(ext):
        raise SystemExit("ERROR: falta kit/extension.dex")
    with zipfile.ZipFile(apk, "r") as z:
        names = z.namelist()
    present = {n for n in names if n.startswith("classes") and n.endswith(".dex")}
    n = 2
    while f"classes{n}.dex" in present:
        n += 1
    dest = f"classes{n}.dex"
    # verificar duplicados: inventario de cada dex del apk + extension
    inv = os.path.join(kit, "dex_inventario.py")
    if not os.path.exists(inv):
        raise SystemExit("ERROR: falta kit/dex_inventario.py")
    import subprocess
    tmp = tempfile.mkdtemp(prefix="kitdex")
    try:
        with zipfile.ZipFile(apk, "r") as z:
            for c in sorted(present):
                z.extract(c, tmp)
        KNOWN_DUPS = {
            # FragmentActivity soporte: la ruta runtime no la toca (verificado)
            "Lcf;",
            # MainActivity del mod (con swipe-controls): fuera de ruta
            "Lcom/google/android/apps/youtube/app/watchwhile/MainActivity;",
        }
        vistas = {}
        for dex in sorted(present) + ["EXT"]:
            path = os.path.join(tmp, dex) if dex != "EXT" else ext
            r = subprocess.run([sys.executable, inv, path, "-q"],
                               capture_output=True, text=True)
            for line in r.stdout.splitlines():
                cls = line.split("\t")[0]
                quien = dex if dex != "EXT" else "extension.dex"
                if cls in vistas:
                    if cls in KNOWN_DUPS:
                        print(f"dex: duplicada conocida {cls} "
                              f"(gana {vistas[cls]}, fuera de ruta)")
                        continue
                    raise SystemExit(f"ERROR: clase duplicada {cls} en "
                                     f"{vistas[cls]} y {quien}")
                vistas[cls] = quien
        print(f"dex: sin duplicados nuevos ({len(vistas)} clases totales)")
        with zipfile.ZipFile(apk, "a", zipfile.ZIP_DEFLATED) as z:
            z.write(ext, dest)
        print(f"dex: extension inyectada como {dest}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if len(sys.argv) < 4 or sys.argv[1] not in ("smali", "dex"):
        print("Uso: aplicar.py smali <dir_decodificado> <dir_kit>")
        print("     aplicar.py dex   <apk_construida>   <dir_kit>")
        return 2
    if sys.argv[1] == "smali":
        parche_ads(sys.argv[2], sys.argv[3])
        parche_bg(sys.argv[2])
        print("OK: enganches smali aplicados")
    else:
        inyectar_dex(sys.argv[2], sys.argv[3])
        print("OK: dex inyectado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
