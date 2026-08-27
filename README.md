# My Ganesha Desktop Companion

A transparent, always-on-top Windows companion based on Praveen's custom My Ganesha pet.

## Install

1. Extract the complete folder to a permanent location, such as `Documents\My Ganesha`.
2. Double-click `install_my_ganesha.bat`.
3. If Python is missing, press `Y` when the installer offers to install it through Windows Package Manager. After Python finishes installing, close the installer and double-click `install_my_ganesha.bat` once more.
4. If Windows asks, allow PowerShell to create the startup shortcut.

My Ganesha will start immediately and automatically whenever you sign in to Windows.

At startup, Ganesha displays a natural greeting based on the PC's local system time, including early-morning, evening, late-night, and after-midnight greetings. A simple motivating thought is randomly selected from ten Bhagavad Gita verses. The immediately previous thought is excluded, so consecutive launches do not repeat it. The welcome remains for about 10 seconds; only then do the normal animation and independent activity clocks begin.

## Controls

- Left-click My Ganesha: wave and give a clear single-eye wink, then resume the peaceful loop.
- Left-click during sleepiness: wake him fully, cancel the pending yoga, and restart from open-eyed abhaya-hasta.
- Left-click and hold, then move the mouse: drag him anywhere on the screen. His position is saved automatically and restored after restart.
- Right-click: Wave or Exit. Exit plays a wink-and-wave goodbye, then gently fades away.
- Escape: Exit.

The normal loop is: grounded abhaya-hasta for about 15 seconds, floating meditation for about 20 seconds, and grounded laptop work for about 15 seconds.

During floating meditation, the stationary lotus uses a richer rose-pink tone and crisp petal separation comparable to the laptop scene.

Special moments now use independent timers:

- Reading begins every 90–120 seconds and lasts about 10 seconds.
- A mouse visits every 4–5 minutes, walking continuously beneath the lotus for about 9.6 seconds with smooth natural speed variation and a gentle step-bob. Ganesha's whole head, ears, face, and gaze progressively track it from entry to exit before returning forward.
- Every 5–6 minutes he first becomes sleepy for about 8–12 seconds, with a slow yawn, heavy smaller eyes, drowsy blinking, nodding and waking stretch; he then immediately performs yoga, holding each pose for 3 seconds.
- The ladoo moment remains about 8 seconds and occurs every 2¾–3¼ minutes.
- Every 7–8 minutes he closes his eyes and peacefully plays the veena for about 10.8 seconds, nodding gently while his plucking hand moves rhythmically and his other hand travels along the frets.
- Every 14½–15½ minutes, the slow sleepy introduction leads to a separate deep-rest scene instead of yoga: the four transition poses last about 2 seconds each, while the third and fourth sleeping poses alternate for about 22 seconds together. He then wakes yawning and stretching and restarts from abhaya-hasta. The complete pillow scene lasts about 30 seconds.

An activity begins after the current normal pose finishes. If two timers become due together, the oldest waiting activity plays first and the other remains queued.

## Customize

Edit `settings.json` while the app is closed:

- `size_percent`: `70` displays My Ganesha at 70% of the source-frame dimensions.
- `corner`: `top-left`, `top-right`, `bottom-left`, or `bottom-right`.
- `margin_x` and `margin_y`: distance from the screen edges.
- `frame_ms`: animation speed; lower is faster.
- state loop counts: time spent in each behavior.
- `reading_loops`: duration of a complete reading moment.
- `ladoo_loops`: duration of a complete ladoo moment.
- `yoga_frame_ms`: duration of each individual yoga pose; `3000` means 3 seconds.
- `sleepy_frame_ms`: speed of the sleepy sequence; `650` keeps its yawning, heavy-eye blinking, nodding, and stretching deliberately slow.
- `veena_frame_ms` and `veena_loops`: control the tempo and total duration of the veena performance.
- `mouse_frame_ms` and the mouse pause settings control the slower, slightly randomized mouse visit.
- Each activity has `interval_min_seconds` and `interval_max_seconds` settings that control its independent randomized interval.

Run `start_my_ganesha.bat` after saving changes.

## Disable automatic startup

Double-click `remove_from_startup.bat`. This only removes the startup shortcut; it preserves the companion and all settings.

## Requirement

Windows 10/11 and Python 3.10 or newer. The installer creates a private environment and installs Pillow automatically.
