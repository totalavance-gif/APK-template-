# Kit: YouTube sin anuncios + segundo plano

Parches recreados del mod Morphe, reportados al mapeo stock.

## Version necesaria

- Bundle **YouTube 21.47.483-BETA**, versionCode **1561317017**
  (`com.google.android.youtube_21.47.483-BETA-...apkm`).
- Se parchea su `base.apk`. Los enganches usan nombres del mapeo
  stock (`acvk`, `argv`, `adtl`); con otra compilacion `aplicar.py`
  aborta sin tocar nada.

## Contenido

| fichero | que es |
|---|---|
| `aplicar.py` | `smali`: enganches; `dex`: inyecta extension (idempotente) |
| `metodo_ads.smali` | metodo nuevo `patch_filterVideoAdTriggers` |
| `extension.dex` | extension Morphe (ruta runtime: 26 clases + libs) |
| `dex_inventario.py` | verifica duplicados (tolera 2 conocidos, fuera de ruta) |
| `01-sin-anuncios.md` | spec del parche de anuncios |
| `02-segundo-plano.md` | spec del parche de segundo plano |
| `build.yml` | workflow de GitHub Actions |

## Como se construye (Actions, x86_64)

1. Sube este `kit/` a tu repo con Actions.
2. Lanza el workflow `build.yml` con la URL del bundle stock
   (o súbelo como asset y ajusta el paso de descarga).
3. El workflow: extrae `base.apk` -> `apktool d` -> `aplicar.py smali`
   -> `apktool b` -> `aplicar.py dex` -> alinea + firma base y
   **todos los splits con la misma clave** -> artefacto instalable
   (base + splits, p.ej. con SAI / APKMirror Installer).

## Notas honestas

- Sin UI de ajustes: el parche de anuncios **fuerza** `HIDE_VIDEO_ADS`.
  La lista blanca de canales sigue funcionando.
- Segundo plano no usa ajustes: funciona directo.
- La extension va completa pero la ruta en ejecucion son 26 clases
  morphe + libs estables; 0 toques a base ofuscada (verificado).
- Duplicados conocidos y benignos: `Lcf;` y la `MainActivity` del
  mod (gana la copia stock, ambas fuera de ruta).
- Firma debug del workflow (o la tuya por secrets). Al firmarse
  base + splits con la misma clave, el conjunto instala junto.
