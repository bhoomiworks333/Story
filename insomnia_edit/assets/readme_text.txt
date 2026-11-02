Insomnia

Keep your Mac awake. Give the session an end time.

A macOS menu bar app for timed awake sessions. Insomnia is an eye icon that lives in your MacBook menu bar. It has no Dock icon and no main window. Set how long your Mac stays awake, choose what happens when the lid closes, and see when something could not be undone.

Website · Install · Using it · Lid close · Recovery · Security

  

Use a stable, well-ventilated surface, not a closed bag. Insomnia is experimental. Recovery can fail, and a running timer is not a safety guarantee. Validation status · Apple's ventilation guidance

Install

Requires macOS 26 or later on an Apple Silicon Mac.

Paste this into your coding agent:

Install the latest stable Insomnia release by following https://github.com/krishhgg/Insomnia/blob/main/skills/install-insomnia/SKILL.md. If a step needs my password, give me the command to run in Terminal.


For the newest nightly, write "the newest Insomnia nightly prerelease" in place of "the latest stable Insomnia release". Nightlies are built from main on each day it has new commits. They have the newest code and may be broken.

To install a release yourself, follow docs/install.md. It covers both channels, how to check the download, and v0.1.0, which installs differently. Settings > App shows the installed version, and "Check for updates" there tells you whether a newer release exists without installing anything.

Build from source

Needs Xcode with Swift 6.2 or later. Replace v<version> with the latest stable tag, or a nightly tag for the newest code:

git clone --branch v<version> --depth 1 https://github.com/krishhgg/Insomnia.git
cd Insomnia
./scripts/install.sh
open "$HOME/Applications/Insomnia.app"
What the installer changes on your Mac
Using it
Start. Click the eye in the menu bar, enter days, hours and minutes, and press Enter.
Add time. Click the eye or the countdown during a session.
End early. Press and hold the end control next to the countdown.
Settings and status. Right-click the eye. Quit asks Insomnia to undo the session first, and it refuses while a change is still waiting to be undone. Saved audio for an output that isn't connected doesn't hold it up. Insomnia restores that output if it reconnects while the app runs, or at the next launch.

You don't have to close the lid, and opening it doesn't end the session.

On battery power, Insomnia turns on Low Power Mode below 40% and ends the session below 10%. Those are the defaults. You can change both in Settings, and an end floor of 0 turns the battery end off. The heat rules turn on Low Power Mode when the Mac gets seriously hot and end the session at critical heat. They are on by default, and Settings can turn them off. All of these rules only work while the app runs.

Before your first session, check Settings. Then run a short session you can watch, and read ~/Library/Logs/Insomnia/insomnia.log afterward.

What happens when the lid closes

During a session, closing the lid does each of these, and opening it tries to undo them. The timer keeps counting down while the lid is closed.

Display and keyboard light go off. Insomnia saves their brightness first. With sleep turned off, macOS no longer does this by itself.
Apps on the freeze list are frozen. Freezing sends an app's processes SIGSTOP, which pauses them until SIGCONT on lid open. The list starts with Slack, WhatsApp and Discord. "Freeze every other app" is off by default. Even when on, it skips meeting, recording and dictation apps: Zoom, Teams, Webex, FaceTime, Wispr Flow, Granola, Otter, OBS and Loom.
Audio is muted. Lid open unmutes each output Insomnia muted, even if you switched to another one.
Low Power Mode turns on. It turns off when the lid opens, unless a battery or heat rule still needs it.
Docker Desktop is frozen when no container runs. This one is off by default.

On Mac laptops with Apple silicon or a T2 chip, closing the lid disconnects the built-in microphone in hardware. Recording a meeting with the lid closed needs AirPods or an external mic.

docs/lid-close.md has the details: how Docker is checked, how brightness is restored, the one-time settings change when you upgrade, and how to test lid actions without closing the lid.

How recovery works

Insomnia writes each change to a recovery journal, a file on disk, before it makes the change. Ending the session tries to undo what the journal lists. If the app crashes or quits, the recovery agent tries the same once the session's end time has passed.

Some things need you:

The recovery agent can't restore audio. Open Insomnia again for that.
The recovery agent doesn't watch the battery or the temperature.
Insomnia only unfreezes a process it can prove it froze. A frozen process it can't prove stays frozen until you check it.

If the menu shows a recovery warning, deal with it before you leave the Mac alone. docs/recovery.md explains each case.

Optional extras
iPhone hotspot handoff and tmux
Chrome, Chromium, Arc and Comet throttling
Configuration and privacy
Uninstall

From your checkout:

./scripts/uninstall.sh          # removes the app, the agent and the sudoers rule
./scripts/uninstall.sh --purge  # also removes settings and logs

From an unpacked release zip, run ./uninstall.sh in its folder instead. The uninstaller undoes any open session first and stops if it can't. docs/install.md has the details.

Development
swift build
swift test

The tests use fakes and temporary folders, so they never change your power settings. See Contributing, Security reporting, Release validation and Design notes.

Star history
License

MIT