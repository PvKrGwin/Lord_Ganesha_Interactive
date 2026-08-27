from __future__ import annotations

import json
import os
import random
import sys
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from pathlib import Path

from PIL import Image, ImageTk


APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
CONFIG_PATH = APP_DIR / "settings.json"
# Tk on Windows removes one exact colour from the companion window.  The frame
# preparation below converts the soft alpha edge into a clean binary mask, so
# this deliberately unusual key colour disappears without bleeding into the
# artwork or adding a second dark outline.
TRANSPARENT = "#ff00ff"
TRANSPARENT_RGB = (0xFF, 0x00, 0xFF)
TRANSPARENCY_ALPHA_CUTOFF = 96

DEFAULTS = {
    "size_percent": 70,
    "corner": "top-left",
    "margin_x": 18,
    "margin_y": 18,
    "frame_ms": 235,
    "idle_loops": 11,
    "meditation_loops": 14,
    "laptop_loops": 11,
    "reading_loops": 7,
    "ladoo_loops": 6,
    "sleepy_frame_ms": 650,
    "veena_frame_ms": 900,
    "veena_loops": 2,
    "deep_sleep_pose_ms": [2000, 2000, 11000, 11000, 2000, 2000],
    "yoga_frame_ms": 3000,
    "mouse_frame_ms": 320,
    "mouse_pause_min_ms": 0,
    "mouse_pause_max_ms": 0,
    "reading_interval_min_seconds": 90,
    "reading_interval_max_seconds": 120,
    "mouse_interval_min_seconds": 240,
    "mouse_interval_max_seconds": 300,
    "yoga_interval_min_seconds": 300,
    "yoga_interval_max_seconds": 360,
    "ladoo_interval_min_seconds": 165,
    "ladoo_interval_max_seconds": 195,
    "veena_interval_min_seconds": 420,
    "veena_interval_max_seconds": 480,
    "deep_sleep_interval_min_seconds": 870,
    "deep_sleep_interval_max_seconds": 930,
    "startup_greeting_seconds": 18,
    "walk_frame_ms": 1500,
    "mahabharata_frame_ms": 1200,
    "mahabharata_loops": 2,
    "walk_interval_min_seconds": 480,
    "walk_interval_max_seconds": 600,
    "mahabharata_interval_min_seconds": 600,
    "mahabharata_interval_max_seconds": 720,
}

STATE_ROWS = {
    "idle": "idle",
    "meditation": "meditation",
    "laptop": "laptop",
    "wave": "wave",
    "yoga": "yoga",
    "sleepy": "sleepy",
    "mouse": "mouse",
    "reading": "reading",
    "ladoo": "ladoo",
    "veena": "veena",
    "deep_sleep": "deep_sleep",
    "walk": "walk",
    "mahabharata": "mahabharata",
}


def prepare_keyed_frame(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize an RGBA sprite and prepare a fringe-free Windows colour key."""
    # Resize premultiplied colour channels so transparent source pixels cannot
    # introduce a dark halo.  Then make the outer edge fully opaque or fully
    # transparent because Tk's Windows colour key has no partial transparency.
    resized = (
        image.convert("RGBa")
        .resize(size, Image.Resampling.LANCZOS)
        .convert("RGBA")
    )
    alpha_mask = resized.getchannel("A").point(
        lambda value: 255 if value >= TRANSPARENCY_ALPHA_CUTOFF else 0
    )
    keyed = Image.new("RGB", resized.size, TRANSPARENT_RGB)
    keyed.paste(resized.convert("RGB"), mask=alpha_mask)
    return keyed


def load_settings() -> dict:
    settings = DEFAULTS.copy()
    if CONFIG_PATH.exists():
        try:
            settings.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return settings


class GaneshaCompanion:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.root = tk.Tk()
        self.root.title("My Ganesha")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT)

        scale = max(20, min(300, int(self.settings["size_percent"]))) / 100.0
        self.width = round(192 * scale)
        self.height = round(208 * scale)
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=TRANSPARENT,
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack()
        self.item = self.canvas.create_image(self.width // 2, self.height // 2)

        self.frames = {
            state: self._load_frames(folder, scale)
            for state, folder in STATE_ROWS.items()
        }
        self.sequence = [
            ("idle", int(self.settings["idle_loops"])),
            ("meditation", int(self.settings["meditation_loops"])),
            ("laptop", int(self.settings["laptop_loops"])),
        ]
        self.sequence_index = 0
        self.state = self.sequence[0][0]
        self.loops_remaining = self.sequence[0][1]
        self.frame_index = 0
        self.wave_requested = False
        self.exit_requested = False
        self.started_at = None
        # Activity clocks begin only after the startup blessing has finished,
        # so the greeting never consumes time from the approved schedules.
        self.next_activity_at = {}
        self.pending_after_special = None
        self.drag_start_pointer = None
        self.drag_start_window = None
        self.dragged = False
        self.mouse_pause_frame = 0
        self.mouse_pause_ms = 0
        self.mouse_pause_used = False
        self.walk_origin = None

        self._place_window()
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._end_drag)
        self.canvas.bind("<Button-3>", self._show_menu)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="Wave", command=self._request_wave)
        self.menu.add_separator()
        self.menu.add_command(label="Exit My Ganesha", command=self._request_exit)

        self._show_startup_greeting()

    def _show_startup_greeting(self) -> None:
        hour = datetime.now().hour
        greetings = (
            (0, 4, ("A peaceful midnight to you", "Still awake? May this quiet night bring you peace")),
            (4, 6, ("A peaceful early morning to you", "A beautiful new day is beginning")),
            (6, 12, ("Good morning", "A very good morning to you")),
            (12, 17, ("Good afternoon", "A bright afternoon to you")),
            (17, 21, ("Good evening", "A peaceful evening to you")),
            (21, 24, ("Good night", "Wishing you a calm and peaceful night")),
        )
        salutation = next(
            random.choice(options)
            for start, end, options in greetings
            if start <= hour < end
        )

        gita_thoughts = (
            ("Focus on your effort, not only on the result.", "Bhagavad Gita 2.47"),
            ("Stay balanced in success and failure.", "Bhagavad Gita 2.48"),
            ("True yoga is doing every action with care and skill.", "Bhagavad Gita 2.50"),
            ("Do your duty sincerely, without being attached to the outcome.", "Bhagavad Gita 3.19"),
            ("Knowledge brings clarity and purifies the mind.", "Bhagavad Gita 4.38"),
            ("Lift yourself through your own thoughts and efforts.", "Bhagavad Gita 6.5"),
            ("Whenever the mind wanders, gently bring it back.", "Bhagavad Gita 6.26"),
            ("A peaceful person neither troubles others nor is troubled by them.", "Bhagavad Gita 12.15"),
            ("Your faith shapes the person you become.", "Bhagavad Gita 17.3"),
            ("Take refuge in the Divine and do not be afraid.", "Bhagavad Gita 18.66"),
        )
        previous_quote = int(self.settings.get("last_gita_quote_index", -1))
        choices = [index for index in range(len(gita_thoughts)) if index != previous_quote]
        quote_index = random.choice(choices)
        quote, verse = gita_thoughts[quote_index]
        self.settings["last_gita_quote_index"] = quote_index
        try:
            CONFIG_PATH.write_text(
                json.dumps(self.settings, indent=2) + "\n", encoding="utf-8"
            )
        except OSError:
            pass

        self.canvas.itemconfigure(self.item, image=self.frames["idle"][0])
        self.greeting = tk.Toplevel(self.root)
        self.greeting.overrideredirect(True)
        self.greeting.attributes("-topmost", True)
        self.greeting.configure(bg="#6f4a20")

        message = (
            f"{salutation}, Praveen!\n\n"
            f"“{quote}”\n"
            f"— {verse}"
        )
        label = tk.Label(
            self.greeting,
            text=message,
            justify="center",
            wraplength=340,
            bg="#fff7dc",
            fg="#5a3517",
            font=("Segoe UI", 10),
            padx=16,
            pady=12,
        )
        label.pack(padx=2, pady=2)

        self.root.update_idletasks()
        self.greeting.update_idletasks()
        bubble_w = self.greeting.winfo_reqwidth()
        bubble_h = self.greeting.winfo_reqheight()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        right_x = root_x + self.width + 8
        bubble_x = right_x if right_x + bubble_w <= screen_w else max(0, root_x - bubble_w - 8)
        bubble_y = max(0, min(root_y + (self.height - bubble_h) // 2, screen_h - bubble_h))
        self.greeting.geometry(f"+{bubble_x}+{bubble_y}")

        duration_ms = max(1, int(float(self.settings["startup_greeting_seconds"]) * 1000))
        self.root.after(duration_ms, self._begin_normal_routine)

    def _begin_normal_routine(self) -> None:
        if hasattr(self, "greeting") and self.greeting.winfo_exists():
            self.greeting.destroy()
        self.started_at = time.monotonic()
        for activity in (
            "reading", "mouse", "yoga", "ladoo", "veena", "deep_sleep",
            "walk", "mahabharata",
        ):
            self._schedule_activity(activity, self.started_at)
        self._tick()

    def _load_frames(self, folder: str, scale: float) -> list[ImageTk.PhotoImage]:
        paths = sorted((ASSET_DIR / folder).glob("*.png"))
        if not paths:
            raise RuntimeError(f"Missing animation frames: {folder}")
        result = []
        for path in paths:
            image = Image.open(path).convert("RGBA")
            keyed = prepare_keyed_frame(image, (self.width, self.height))
            result.append(ImageTk.PhotoImage(keyed))
        return result

    def _place_window(self) -> None:
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        saved_x = self.settings.get("position_x")
        saved_y = self.settings.get("position_y")
        if saved_x is not None and saved_y is not None:
            x = max(0, min(int(saved_x), screen_w - self.width))
            y = max(0, min(int(saved_y), screen_h - self.height))
            self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
            return
        margin_x = int(self.settings["margin_x"])
        margin_y = int(self.settings["margin_y"])
        corner = str(self.settings["corner"]).lower()
        x = screen_w - self.width - margin_x if "right" in corner else margin_x
        y = screen_h - self.height - margin_y if "bottom" in corner else margin_y
        self.root.geometry(f"{self.width}x{self.height}+{max(0, x)}+{max(0, y)}")

    def _request_wave(self, _event=None) -> None:
        if self.state == "sleepy":
            # A click gently wakes him fully, cancels the yoga that would have
            # followed this sleepy interlude, and restarts the normal cycle.
            self.wave_requested = False
            self.pending_after_special = None
            self.sequence_index = 0
            state, loops = self.sequence[self.sequence_index]
            self._set_state(state, loops)
            self.canvas.itemconfigure(self.item, image=self.frames[state][0])
            return
        self.wave_requested = True

    def _request_exit(self) -> None:
        if self.exit_requested:
            return
        self.exit_requested = True
        self.wave_requested = False
        self.pending_after_special = None
        self._set_state("wave", 1)

    def _fade_and_exit(self, step: int = 10) -> None:
        if step <= 0:
            self.root.destroy()
            return
        self.root.attributes("-alpha", step / 10)
        self.root.after(60, lambda: self._fade_and_exit(step - 1))

    def _start_drag(self, event) -> None:
        self.drag_start_pointer = (event.x_root, event.y_root)
        self.drag_start_window = (self.root.winfo_x(), self.root.winfo_y())
        self.dragged = False

    def _drag(self, event) -> None:
        if self.drag_start_pointer is None or self.drag_start_window is None:
            return
        delta_x = event.x_root - self.drag_start_pointer[0]
        delta_y = event.y_root - self.drag_start_pointer[1]
        if abs(delta_x) + abs(delta_y) >= 5:
            self.dragged = True
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, min(self.drag_start_window[0] + delta_x, screen_w - self.width))
        y = max(0, min(self.drag_start_window[1] + delta_y, screen_h - self.height))
        self.root.geometry(f"+{x}+{y}")

    def _end_drag(self, _event) -> None:
        if self.dragged:
            self.settings["position_x"] = self.root.winfo_x()
            self.settings["position_y"] = self.root.winfo_y()
            try:
                CONFIG_PATH.write_text(
                    json.dumps(self.settings, indent=2) + "\n", encoding="utf-8"
                )
            except OSError:
                pass
        else:
            self._request_wave()
        self.drag_start_pointer = None
        self.drag_start_window = None
        self.dragged = False

    def _show_menu(self, event) -> None:
        self.menu.tk_popup(event.x_root, event.y_root)

    def _set_state(self, state: str, loops: int = 1) -> None:
        self.state = state
        self.frame_index = 0
        self.loops_remaining = max(1, loops)
        if state == "mouse":
            self.mouse_pause_frame = random.randint(2, 5)
            self.mouse_pause_ms = random.randint(
                int(self.settings["mouse_pause_min_ms"]),
                int(self.settings["mouse_pause_max_ms"]),
            )
            self.mouse_pause_used = False
        elif state == "walk":
            self.walk_origin = (self.root.winfo_x(), self.root.winfo_y())

    def _advance_cycle(self) -> None:
        self.sequence_index = (self.sequence_index + 1) % len(self.sequence)
        state, loops = self.sequence[self.sequence_index]
        self._set_state(state, loops)

    def _schedule_activity(self, activity: str, from_time: float) -> None:
        minimum = float(self.settings[f"{activity}_interval_min_seconds"])
        maximum = float(self.settings[f"{activity}_interval_max_seconds"])
        if maximum < minimum:
            minimum, maximum = maximum, minimum
        self.next_activity_at[activity] = from_time + random.uniform(minimum, maximum)

    def _maybe_start_timed_activity(self) -> bool:
        now = time.monotonic()
        due = [
            activity
            for activity, due_at in self.next_activity_at.items()
            if now >= due_at
        ]
        if not due:
            return False

        # Play the oldest waiting activity first. Other expired clocks remain
        # due and will run at later normal-state boundaries.
        state = min(due, key=lambda activity: self.next_activity_at[activity])
        self._schedule_activity(state, now)
        if state in {"yoga", "deep_sleep"}:
            self.pending_after_special = state
            self._set_state("sleepy", random.choice((2, 3)))
            return True
        loops = {
            "reading": int(self.settings["reading_loops"]),
            "ladoo": int(self.settings["ladoo_loops"]),
            "veena": int(self.settings["veena_loops"]),
            "mahabharata": int(self.settings["mahabharata_loops"]),
        }.get(state, 1)
        self._set_state(state, loops)
        return True

    def _tick(self) -> None:
        if self.wave_requested and self.state != "wave":
            self.wave_requested = False
            self._set_state("wave", 2)

        displayed_state = self.state
        current = self.frames[displayed_state]
        displayed_frame = self.frame_index
        self.canvas.itemconfigure(self.item, image=current[displayed_frame])

        if displayed_state == "walk" and self.walk_origin is not None:
            # Move out for the first half of the scene, then return precisely
            # to the saved starting point. One quarter of the usable screen is
            # enough to feel like a journey without losing the companion.
            progress = displayed_frame / max(1, len(current) - 1)
            outward = progress * 2 if progress <= 0.5 else (1.0 - progress) * 2
            screen_w = self.root.winfo_screenwidth()
            max_travel = max(0, (screen_w - self.width) // 4)
            direction = 1
            if self.walk_origin[0] + max_travel > screen_w - self.width:
                direction = -1
            x = self.walk_origin[0] + round(direction * max_travel * outward)
            self.root.geometry(f"+{x}+{self.walk_origin[1]}")
        self.frame_index += 1

        if self.frame_index >= len(current):
            self.frame_index = 0
            self.loops_remaining -= 1
            if self.loops_remaining <= 0:
                if self.state in {
                    "wave", "yoga", "sleepy", "mouse", "reading", "ladoo", "veena",
                    "deep_sleep", "walk", "mahabharata"
                }:
                    if self.state == "wave" and self.exit_requested:
                        self._fade_and_exit()
                        return
                    if self.state == "sleepy" and self.pending_after_special in {"yoga", "deep_sleep"}:
                        next_state = self.pending_after_special
                        self.pending_after_special = None
                        self._set_state(next_state, 1)
                    elif self.state == "deep_sleep":
                        self.sequence_index = 0
                        state, loops = self.sequence[0]
                        self._set_state(state, loops)
                    elif self.state == "walk":
                        if self.walk_origin is not None:
                            self.root.geometry(f"+{self.walk_origin[0]}+{self.walk_origin[1]}")
                        self.walk_origin = None
                        state, loops = self.sequence[self.sequence_index]
                        self._set_state(state, loops)
                    else:
                        state, loops = self.sequence[self.sequence_index]
                        self._set_state(state, loops)
                else:
                    if not self._maybe_start_timed_activity():
                        self._advance_cycle()

        if displayed_state == "deep_sleep":
            pose_times = self.settings["deep_sleep_pose_ms"]
            delay = int(pose_times[min(displayed_frame, len(pose_times) - 1)])
        elif displayed_state == "veena":
            delay = int(self.settings["veena_frame_ms"])
        elif displayed_state == "sleepy":
            delay = int(self.settings["sleepy_frame_ms"])
        elif displayed_state == "yoga":
            delay = int(self.settings["yoga_frame_ms"])
        elif displayed_state == "mouse":
            delay = int(self.settings["mouse_frame_ms"])
            if (
                displayed_frame == self.mouse_pause_frame
                and not self.mouse_pause_used
            ):
                delay += self.mouse_pause_ms
                self.mouse_pause_used = True
        elif displayed_state == "walk":
            delay = int(self.settings["walk_frame_ms"])
        elif displayed_state == "mahabharata":
            delay = int(self.settings["mahabharata_frame_ms"])
        else:
            delay = int(self.settings["frame_ms"])
        self.root.after(delay, self._tick)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    try:
        GaneshaCompanion().run()
    except Exception as exc:
        messagebox.showerror("My Ganesha", str(exc))
        raise
