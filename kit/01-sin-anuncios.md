# Parche 1 — Sin anuncios de video (mapeo stock 1561317017)

- **Base**: `base.apk` del bundle YouTube **21.47.483-BETA**
  (versionCode **1561317017**). El mod trae otro mapeo ofuscado;
  estos nombres son los del stock, verificados por estructura
  (similitud 95% con el metodo original del mod).
- **Efecto**: si el ajuste esta activo, filtra los triggers de
  anuncio de video y `t()` sale antes de programarlos.

## Ficheros nuevos

`extension.dex` del kit inyectado como `classesN.dex` libre
(ver `aplicar.py dex`). Aporta `AdsPatch` + su ruta (26 clases).

## Edicion A — metodo nuevo en `acvk.smali`

Anadir al final de la clase (texto en `metodo_ads.smali`):

```smali
.method private static patch_filterVideoAdTriggers(Ljava/util/List;)Ljava/util/List;
    .registers 6

    # El kit no trae UI de ajustes: se fuerza el flag.
    const/4 v5, 0x1

    sput-boolean v5, Lapp/morphe/extension/youtube/patches/ads/AdsPatch;->HIDE_VIDEO_ADS:Z

    invoke-static {}, Lapp/morphe/extension/youtube/patches/ads/AdsPatch;->hideVideoAds()Z

    move-result v0

    if-eqz v0, :cond_26

    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    invoke-interface {p0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v1

    const/16 v4, 0x6

    :cond_11
    :goto_11
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_25

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ladtl;

    iget v3, v2, Ladtl;->a:I

    if-ne v3, v4, :cond_11

    invoke-interface {v0, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_11

    :cond_25
    return-object v0

    :cond_26
    return-object p0
.end method
```

(`Ladtl;` es el `Ladht;` del mod en este mapeo: misma forma,
5 metodos, campo `a:I`.)

## Edicion B — inicio de `acvk.t(Ljava/util/List;)V`

Huella: `move-object/from16 v1, p0` seguido de
`new-instance v2, Landroid/util/SparseArray;`. Insertar ANTES:

```smali
    invoke-static/range {p1 .. p1}, Lacvk;->patch_filterVideoAdTriggers(Ljava/util/List;)Ljava/util/List;

    move-result-object p1

    invoke-static {}, Lapp/morphe/extension/youtube/patches/ads/AdsPatch;->hideVideoAds()Z

    move-result v0

    if-eqz v0, :cond_b

    return-void

    :cond_b
    nop
```

`v0` es scratch a la entrada: no hace falta subir `.registers`.
