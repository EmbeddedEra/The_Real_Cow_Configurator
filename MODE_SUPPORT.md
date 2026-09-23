# Remote operating mode

Unified Cow Remote6.16.0 adds Normal/Recording selection under Remote Settings.
The selector appears only when a complete DUMP reports valid MODE, ACTIVE_MODE,
SAVED_MODE and DUMP_END fields. Older remote firmware and robots never receive MODE.

Select a mode, Save, then power the remote off and on. Active mode stays unchanged
until restart. The app checks the mode echo, SAVE_OK, then LOAD_OK and a fresh DUMP
before reporting a verified mode save. Default Reset saves Normal for the next
restart. Load discards pending device settings. The initial connection only reads
DUMP, preserving an already-staged setting. Imports validate NORMAL/RECORDING;
exports include the selected mode but not runtime active/saved status.

Busy/error replies stop the operation. Earlier settings may already be staged;
the app does not claim rollback. Missing required replies invalidate the serial
session to prevent a late acknowledgement being mistaken for the next operation;
reconnect and load settings before retrying. Legacy firmware has silent commands,
so its upload reports that settings were sent and asks for a load to verify.

The page keeps its single-file/offline design. One continuous reader collects
fragmented lines; transactions serialize commands with real deadlines. Diagnostic
polls cannot accumulate an unbounded queue. Mode UI capability resets on reconnect.

Run offline browser integration checks with Python and Playwright Chromium:

```sh
uv run --with playwright==1.62.0 playwright install chromium
uv run --with playwright==1.62.0 python tests/browser_mode.py
```

Tests mock Web Serial and cover split DUMP responses, save/restart/reset,
busy/errors/missing acknowledgement, import/export, older firmware, robot mode,
and diagnostic transaction timing. Real USB/hardware verification remains needed.
The existing semantic-release workflow assigns the app version when merged to main.
