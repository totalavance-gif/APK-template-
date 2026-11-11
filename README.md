# APK-template

Plantilla mínima de app Android (Java, sin dependencias) + workflow de GitHub Actions
que compila el APK de debug en cada push a `main`.

## Descargar el APK

1. Abre la pestaña **Actions** del repo.
2. Entra al último run verde de **Build APK**.
3. Descarga el artifact **app-debug** (contiene `app-debug.apk`).

Si un build falla, el workflow abre un issue automáticamente con el extracto del log.

## Usar la plantilla

- Marca el repo como template (Settings → Template repository) o clónalo.
- Ábrelo en Android Studio (genera `local.properties` con tu SDK; ese archivo no se sube).
- Cambia `applicationId` y `namespace` en `app/build.gradle` y el paquete de `MainActivity`.
- Cada push a `main` compila y publica el APK solo.

## Requisitos

- JDK 17 (el CI lo instala solo).
- Android SDK con `compileSdk 34` para compilar en local.

## Estructura

```
├── settings.gradle / build.gradle / gradle.properties
├── gradlew (+ gradle/wrapper)   # wrapper fijado a Gradle 8.9
├── app/
│   ├── build.gradle             # AGP 8.5.2, minSdk 24, Java 17
│   └── src/main/                # Manifest + MainActivity + recursos
└── .github/workflows/build-apk.yml
```

## Siguiente paso: APK release firmado

Crea un keystore (`keytool -genkeypair`), añade `signingConfigs` en `app/build.gradle`
leyendo la clave desde secretos, y guarda el keystore como secreto de Actions.
Sin eso, `assembleRelease` genera un APK sin firmar.
