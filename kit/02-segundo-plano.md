# Parche 2 — Reproduccion en segundo plano (mapeo stock 1561317017)

- **Base**: `base.apk` del bundle YouTube **21.47.483-BETA**
  (versionCode **1561317017**).
- **Efecto**: `argv.B()` delega en el mod si se permite el segundo
  plano (el mod dice que si, salvo Shorts cerrado o mini-inline).

## Ficheros nuevos

`extension.dex` (igual que parche 1).

## Edicion — return de `argv.B(Lbhsd;)Z`

Huella de mapeo en el cuerpo: `Lbdow;->c:Z` (el gate boolean;
equivale al `Lbcch;->c:Z` del mod) y firma
`.method public static B(Lbhsd;)Z`.

El metodo tiene una sola salida:

```smali
    :cond_30
    return v0
```

Reemplazarla por:

```smali
    :cond_30
    invoke-static {v0}, Lapp/morphe/extension/youtube/patches/misc/BackgroundPlaybackPatch;->isBackgroundPlaybackAllowed(Z)Z

    move-result v0

    return v0
```

No cambian firmas ni `.registers`: solo se envuelve el return.
(`Lbhsd;`/`Lbhru;`/`Lbdow;` son `Lbgef;`/`Lbgdw;`/`Lbcch;` del mod.)
