# Building Kix as an Android APK

This guide packages Kix into a debug APK using [Buildozer](https://github.com/buildozer/buildozer) + [python-for-android](https://github.com/kivy/python-for-android).

## Two ways to get an APK

### A. Download a pre-built APK (no toolchain required)

Push a version tag and let GitHub Actions build it for you:

```bash
git tag v0.1.0
git push --tags
```

Then open the Actions tab in your browser, wait for the run to finish, and download `kix-debug-v0.1.0` from the workflow run's **Artifacts** section. Transfer it to your phone and install it.

You can also trigger a build without a tag via the Actions tab → **Run workflow** → **Run workflow**.

First build on a clean runner: 20–40 min (downloads Android SDK + NDK). Cached builds: 5–15 min.

### Trigger a build from your phone

You can do everything from a mobile browser:

1. **Create the tag from GitHub's web UI** — go to the repository → **Releases** → **Draft a new release**. Type `v0.1.0` in "Choose a tag", publish it. This triggers the workflow.
2. **Watch progress** — repository → **Actions** → the run appears. Refresh to see build logs.
3. **Download the APK** — at the bottom of the run page, under **Artifacts**, tap `kix-debug-v0.1.0`. Your phone downloads the `.apk` file.
4. **Install** — tap the downloaded file. Android will ask you to allow installation from this source (Settings → "Install unknown apps" → enable for your browser).

You can also trigger a build manually without a tag: **Actions** → **Android APK** → **Run workflow** → **Run workflow**.

### B. Build it locally on a desktop

```bash
make install-tools
make icon
make android-debug
```

The first run downloads ~3 GB of Android SDK/NDK into `.buildozer/` and takes 20–40 minutes. Subsequent builds are 30 s – 5 min unless you change `requirements` or `p4a.bootstrap` in `buildozer.spec`.

## Prerequisites

### Linux (Ubuntu / Debian)

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv \
    build-essential ccache git libffi-dev libssl-dev \
    libjpeg-dev libpng-dev zlib1g-dev libfreetype6-dev \
    libsqlite3-dev libstdc++6 openjdk-17-jdk-headless autoconf \
    libtool pkg-config unzip zip
```

### macOS

```bash
xcode-select --install            # Xcode Command Line Tools
brew install python@3.11 openjdk@17
```

### Windows

**Not supported natively.** Use WSL2 with Ubuntu:

```powershell
wsl --install -d Ubuntu
# Then follow the Linux instructions inside WSL.
```

## Where the APK lands

After a successful `make android-debug`:

```
.buildozer/android/platform/build-<p4a-version>/dists/kix/builds/android/<arch>/kix-0.1.0-debug.apk
```

`<arch>` is `arm64-v8a` for most modern phones. There is also `armeabi-v7a`, `x86`, `x86_64` if you set `android.archs` accordingly.

## Installing on a device

With `adb` installed and USB debugging enabled on the phone:

```bash
adb devices                                                # confirm the phone is listed
adb install -r .buildozer/android/platform/build-*/dists/kix/builds/android/*/kix-0.1.0-debug.apk
adb shell am start -n org.kix.kix/org.kivy.android.PythonActivity
```

Or transfer the `.apk` to the device and tap it (you may need to enable "Install from unknown sources" in Settings).

## Release signing

`make android-release` will produce an unsigned APK that Android refuses to install. To sign it:

1. Generate a keystore (one-time):
   ```bash
   keytool -genkey -v -keystore kix.keystore -alias kix \
       -keyalg RSA -keysize 2048 -validity 10000
   ```
2. Fill in the four `android.keystore*` lines at the bottom of `buildozer.spec`.
3. **Do not commit the keystore or its passwords.** Add `kix.keystore` to `.gitignore` and use a CI secret / environment variable for the passwords.

For Play Store distribution you'll also want an `.aab` (App Bundle) instead of an `.apk`:

```bash
buildozer android aab
```

## Permissions reference

All permissions are declared at **install time** in `buildozer.spec` (no runtime `PermissionRequester` flow exists yet — Kix's sensor blocks are stubs that return dataclass defaults today).

| Block category                  | Permission(s)                                                | Notes                                                                 |
|---------------------------------|--------------------------------------------------------------|-----------------------------------------------------------------------|
| `gps`, location                 | `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`             | install-time                                                          |
| `camera`, `face`, `ocr`         | `CAMERA`                                                     | install-time; runtime request TODO                                    |
| `microphone`, `speech`          | `RECORD_AUDIO`                                               | install-time; runtime request TODO                                    |
| `nfc`                           | `NFC`                                                        | install-time                                                          |
| `vibrate`                      | `VIBRATE`                                                    | install-time                                                          |
| `nxt`, `arduino`, `makey-makey`| `BLUETOOTH`, `BLUETOOTH_ADMIN`, `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN` | install-time; runtime request TODO on Android 12+              |
| `http`, `tcp`, `udp`, `websocket` | `INTERNET`                                                | install-time                                                          |
| `file_*`, `open_*`, `save_*`    | `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `MANAGE_EXTERNAL_STORAGE` | install-time; API 33+ scoped storage applies when implemented |
| `notification`                 | *(none yet — `POST_NOTIFICATIONS` is API 33+ runtime)*       | runtime TODO                                                          |

If you implement a real sensor bridge, add runtime permission requests via `pyjnius` + `android.permission.PermissionRequester`. Until then, the install-time grant is enough for the stubs.

## Troubleshooting

### "Cython version not supported" / "Cython 3.x is not supported"

Run `make install-tools` to pin Cython to 3.0.10 — this is the documented fix.

### "Android SDK license not accepted"

```bash
yes | ~/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
```

### "gcc: command not found" / recipe build failures

Install the Linux apt block above (`build-essential`, `libffi-dev`, `libssl-dev`, etc.) — top three missing-lib causes are gcc, libffi-dev, and openjdk-17-jdk-headless.

### First build hangs on "Installing Python for android"

Expected on first run (downloads the p4a bootstrap tarball, ~400 MB). Subsequent runs are fast.

### App crashes immediately on launch

Plug the phone in and read the logcat:

```bash
adb logcat | grep -iE 'python|kivy|kix'
```

Look for `ModuleNotFoundError` — that means `requirements = …` in `buildozer.spec` is missing a Python package your code imports.

## What runs in the APK

The packaged app is functionally identical to `python3 -m Kix.main` on desktop — same theme, same Dashboard, same Editor with 5 tabs, same 320+ blocks. Hardware/sensor blocks (`Kix/blocks/sensors.py`, `hardware.py`, `audio_advanced.py`, `arvr.py`) are currently stubs; the APK declares the permissions so the install is correct, but the blocks return defaults until a real Android JNI bridge is implemented. See `Kix/README.md` for the full feature list.

## Files this guide references

- `buildozer.spec` — single source of truth for the Android packaging pipeline.
- `Makefile` — `make install-tools`, `make icon`, `make android-debug`, etc.
- `tools/make_icon.py` — idempotent launcher-icon generator (Pillow).
- `Kix/assets/icons/kix.png` — generated launcher icon (512×512).