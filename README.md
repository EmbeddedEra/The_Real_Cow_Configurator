# The Real Cow Configurator

Browser-based USB configuration for EmbeddedEra Cow remotes and robot receivers, using Web Serial.

**[Open the Configurator](https://embeddedera.github.io/The_Real_Cow_Configurator/)**

## Get started

1. Use a desktop browser with Web Serial support, such as Chrome or Edge.
2. Connect the remote or receiver with a USB data cable, running its normal firmware rather than DFU mode.
3. Click **Connect**, select the device, and wait for identification and settings to load.
4. Adjust settings and use the upload/save button. Use **Load** to retrieve saved settings, or **Default Reset** to restore defaults.

The app enables the appropriate remote or robot settings. Remote options include radio channel, playback stop delay and four maximum-power settings. Robot options include motor and sensor settings and diagnostic views.

## Normal / Recording mode

On compatible unified remote firmware, **Remote Settings → Operating mode** offers Normal and Recording. The app shows the active mode, saved mode and whether a restart is needed.

1. Select a mode while the remote is idle.
2. Save and wait for verification.
3. Power the remote off and on to activate it.

Older remotes and robots do not expose this selector and are never sent mode commands. Default Reset saves Normal on unified firmware, but the active mode remains unchanged until restart. Configuration export/import supports the selected mode without exporting runtime status.

If a command is rejected as busy, release the controls and stop recording/playback before retrying. After a response timeout, reconnect and load settings to check what was saved. Earlier commands may already have changed pending settings; an error does not imply rollback.

See [MODE_SUPPORT.md](MODE_SUPPORT.md) for the USB contract, compatibility behavior and testing details.

## Run locally

This is a static site; no application build or backend is required. From the repository root:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000` in a compatible browser. Web Serial requires a secure context, such as HTTPS or localhost. The app also provides a download of its single HTML page for offline use; browser permissions and externally loaded diagnostic dependencies may still affect offline operation.

## Test

Install [uv](https://github.com/astral-sh/uv), then install the test browser and run the mocked Web Serial checks:

```sh
uv run --with playwright==1.62.0 playwright install chromium
uv run --with playwright==1.62.0 python tests/browser_mode.py
```

The suite checks fragmented replies, mode save/restart/reset, rejected commands, missing acknowledgements, import/export, older firmware and diagnostic polling. It does not connect to or modify a physical device.

## Repository and releases

- [index.html](index.html) — interface, Web Serial transport and configuration logic.
- [MODE_SUPPORT.md](MODE_SUPPORT.md) — operating-mode behavior.
- [tests/browser_mode.py](tests/browser_mode.py) — browser integration checks.
- [.github/workflows/release.yml](.github/workflows/release.yml) — semantic-release workflow on `main`.

GitHub Pages publishes the site. The release workflow updates the displayed app version; avoid manually assigning a conflicting version. The dependencies in `package.json` support release tooling rather than an application build.

## Related projects

- [Cow Remote](https://github.com/EmbeddedEra/Cow_Remote) — firmware and hardware.
- [Cow Flasher](https://embeddedera.github.io/The_Real_Cow_Flasher/) — firmware installation; [source](https://github.com/EmbeddedEra/The_Real_Cow_Flasher).
- [Cow Robot Board](https://github.com/EmbeddedEra/Cow_Robot_Board) — receiver firmware and hardware.
