"""Qtile config."""

import os
import subprocess

from libqtile import bar, hook, layout, qtile, widget
from libqtile.config import (
    Click,
    Drag,
    DropDown,
    Group,
    Key,
    KeyChord,
    Match,
    ScratchPad,
    Screen,
)
from libqtile.lazy import lazy
from libqtile.widget.battery import Battery, BatteryState
from monitors import get_monitors
from xmonad import MonadTall, MonadWide

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.environ["HOME"] + "/.config")


def get_group(group_name):
    """Get group by name."""
    for group in groups:
        if group.name == group_name:
            return group
    return None


def toscreen(qtile, group_name):
    """Sticky screen focus group."""
    group = qtile.groups_map.get(group_name)

    if group is None:
        raise KeyError("Group does not exist", group_name)

    screen_affinity = get_group(group_name).screen_affinity

    if qtile.current_screen.index != screen_affinity and screen_affinity is not None:
        qtile.cmd_to_screen(screen_affinity)

    return qtile.current_screen.set_group(group)


def my_tasklist_parse(text):
    if text.startswith("qute"):
        text = text.split("]", 1)[0] + "]"

    return text


def group_or_app(qtile, group_name, app):
    """Go to specified group if it exists. Otherwise, run the specified app.
    When used in conjunction with dgroups to auto-assign apps to specific
    groups, this can be used as a way to go to an app if it is already
    running."""

    try:
        toscreen(qtile, group_name)
    except KeyError:
        qtile.cmd_spawn(app)


mod = "mod4"
alt = "mod1"
shift = "shift"
ctrl = "control"

terminal = "kitty"
editor = terminal + " zsh -i -c nvim"

colors = {
    "red": "#E06C75",
    "dark_red": "#BE5046",
    "green": "#98C379",
    "yellow": "#E5C07B",
    "dark_yellow": "#D19A66",
    "blue": "#61AFEF",
    "purple": "#C678DD",
    "cyan": "#56B6C2",
    "white": "#ABB2BF",
    "dark_white": "#979EAB",
    "black": "#282C34",
    "comment_grey": "#5C6370",
    "gutter_fg_grey": "#4B5263",
    "cursor_grey": "#2C323C",
    "special_grey": "#3B4048",
    "vertsplit": "#21252B",
}

keys = [
    KeyChord(
        [mod],
        "g",
        [
            Key([mod], "g", lazy.switchgroup()),
            Key([mod], "r", lazy.labelgroup()),
        ],
    ),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod, shift], "j", lazy.layout.shuffle_down()),
    Key([mod, shift], "k", lazy.layout.shuffle_up()),
    Key([mod, ctrl], "j", lazy.group.next_window()),
    Key([mod, ctrl], "k", lazy.group.prev_window()),
    Key([mod], "h", lazy.layout.shrink_master()),
    Key([mod], "l", lazy.layout.grow_master()),
    Key([mod], "n", lazy.layout.normalize()),
    Key([mod, shift], "n", lazy.layout.reset()),
    Key([mod, ctrl], "m", lazy.window.toggle_maximize()),
    Key([mod], "m", lazy.layout.maximize()),
    Key([mod], "y", lazy.layout.flip()),
    Key([mod, shift], "y", lazy.layout.flip_master()),
    Key([mod], "comma", lazy.layout.increase_nmaster()),
    Key([mod], "period", lazy.layout.decrease_nmaster()),
    Key([mod], "space", lazy.layout.master()),
    Key([mod, shift], "space", lazy.layout.swap_master()),
    Key([mod, ctrl], "space", lazy.window.toggle_floating()),
    Key([mod, ctrl], "n", lazy.window.toggle_minimize()),
    Key([mod, ctrl], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "u", lazy.next_urgent()),
    # Focus screens
    Key([mod], "o", lazy.next_screen()),
    Key([mod], "i", lazy.prev_screen()),
    Key([mod], "b", lazy.hide_show_bar()),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod, shift], "Return", lazy.spawn(editor), desc="Launch editor"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, shift], "Tab", lazy.prev_layout(), desc="Toggle between layouts"),
    Key([mod, shift], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, ctrl], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, ctrl], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key(
        [mod],
        "r",
        lazy.spawn("rofi -show combi"),
        desc="Spawn a command using a prompt widget",
    ),
    Key(
        [],
        "XF86AudioPlay",
        lazy.spawn("playerctl play-pause"),
        desc="playerctl play-pause",
    ),
    Key([], "XF86AudioStop", lazy.spawn("playerctl stop"), desc="playerctl stop"),
    Key(
        [],
        "XF86AudioPrev",
        lazy.spawn("playerctl previous"),
        desc="playerctl play-pause",
    ),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next"), desc="playerctl play-pause"),
    Key(
        [],
        "XF86AudioLowerVolume",
        lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -10%"),
        desc="Lower volume",
    ),
    Key(
        [],
        "XF86AudioRaiseVolume",
        lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +10%"),
        desc="Raise volume",
    ),
    Key(
        [],
        "XF86AudioMute",
        lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle"),
        desc="Mute volume",
    ),
    Key(
        [],
        "XF86AudioMicMute",
        lazy.spawn("pactl set-source-mute @DEFAULT_SOURCE@ toggle"),
        desc="Mute microphone",
    ),
]

groups = [Group(i) for i in "1234567890"]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.function(toscreen, i.name),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, ctrl],
                i.name,
                lazy.window.togroup(i.name, switch_group=False),
                desc="Move current window to group {}".format(i.name),
            ),
            Key(
                [mod, shift],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Move current window and switch to group {}".format(i.name),
            ),
            Key(
                [mod, shift, ctrl],
                i.name,
                lazy.group.switch_groups(i.name),
                desc="Move current group to {}".format(i.name),
            ),
        ]
    )

groups.extend(
    [
        Group(
            "chat",
            label=" ",
            persist=False,
            init=False,
            matches=[
                Match(
                    wm_class=[
                        "slack",
                        "Microsoft Teams - Preview",
                        "Zoom Meeting",
                        "Zoom Cloud Meetings",
                    ]
                )
            ],
            screen_affinity=1,
        ),
        Group(
            "www",
            label=" ",
            persist=False,
            init=False,
            matches=[Match(wm_class=["firefox"]), Match(wm_instance_class=["qutebrowser"])],
            screen_affinity=0,
        ),
        Group(
            "edit",
            label=" ",
            persist=False,
            init=False,
            matches=[Match(title=["nvr"]), Match(wm_class=["nvr"])],
            screen_affinity=0,
        ),
        Group(
            "file",
            label=" ",
            persist=False,
            init=False,
            matches=[Match(title=["vifm"]), Match(wm_class=["vifm"])],
        ),
    ]
)
groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "term",
                terminal,
                x=0,
                width=0.998,
                height=0.45,
                warp_pointer=False,
                on_focus_lost_hide=True,
            ),
            DropDown("spotify", "spotify", height=0.8, warp_pointer=False),
        ],
    )
)

keys.extend(
    [
        # Key([mod], "s", lazy.group["chat"].toscreen()),
        Key([mod], "s", lazy.function(group_or_app, "chat", "slack")),
        Key([mod, shift], "s", lazy.window.togroup("chat", switch_group=True)),
        # Key([mod], "w", lazy.group["www"].toscreen()),
        Key([mod], "w", lazy.function(group_or_app, "www", "qutebrowser")),
        Key([mod, shift], "w", lazy.window.togroup("www", switch_group=True)),
        # Key([mod], "e", lazy.group["edit"].toscreen()),
        Key(
            [mod],
            "e",
            lazy.function(
                group_or_app,
                "edit",
                terminal + " --class nvr zsh -i -c 'nvim --listen ~/.cache/nvim/server.pipe'",
            ),
        ),
        Key([mod, shift], "e", lazy.window.togroup("edit", switch_group=True)),
        Key(
            [mod],
            "f",
            lazy.function(group_or_app, "file", terminal + " --class vifm zsh -i -c vifm"),
        ),
        Key([mod, shift], "f", lazy.window.togroup("file", switch_group=True)),
        Key([mod], "t", lazy.group["scratchpad"].dropdown_toggle("term")),
        KeyChord(
            [mod],
            "x",
            [
                Key([mod], "x", lazy.qtilecmd()),
                Key([mod], "s", lazy.group["scratchpad"].dropdown_toggle("spotify")),
            ],
        ),
        KeyChord(
            [mod],
            "z",
            [
                Key(
                    [mod],
                    "u",
                    lazy.spawn(
                        [
                            "sh",
                            "-c",
                            "gopass ls --flat | rofi -dmenu | xargs --no-run-if-empty -I{} -r "
                            "qtile cmd-obj -o cmd -f spawn -a 'gopass show --clip {} username'",
                        ]
                    ),
                ),
                Key(
                    [mod],
                    "p",
                    lazy.spawn(
                        [
                            "sh",
                            "-c",
                            "gopass ls --flat | rofi -dmenu | xargs --no-run-if-empty -I{} -r "
                            "qtile cmd-obj -o cmd -f spawn -a 'gopass show --clip {}'",
                        ]
                    ),
                ),
                Key(
                    [mod],
                    "o",
                    lazy.spawn(
                        [
                            "sh",
                            "-c",
                            "gopass ls --flat | rofi -dmenu | xargs --no-run-if-empty -I{} -r "
                            "qtile cmd-obj -o cmd -f spawn -a 'gopass totp --clip {}'",
                        ]
                    ),
                ),
                Key(
                    [mod],
                    "a",
                    lazy.spawn(
                        [
                            "sh",
                            "-c",
                            "gopass ls --flat | rofi -dmenu | xargs --no-run-if-empty -I{} -r "
                            "qtile cmd-obj -o cmd -f spawn -a 'gopass show --clip {} url'",
                        ]
                    ),
                ),
            ],
        ),
    ]
)

layout_defaults = dict(
    border_focus=colors["blue"],
    border_normal=colors["comment_grey"],
)

layouts = [
    MonadTall(**layout_defaults),
    MonadWide(**layout_defaults),
]

widget_defaults = dict(
    font="MesloLGM Nerd Font",
    fontsize=14,
    padding=3,
    foreground=colors["white"],
)

extension_defaults = widget_defaults.copy()


class MyBattery(Battery):
    """My custom battery widget."""

    def build_string(self, status):
        """Build string for output."""
        if self.layout is not None:
            if status.state == BatteryState.DISCHARGING and status.percent < self.low_percentage:
                self.layout.colour = self.low_foreground
            else:
                self.layout.colour = self.foreground
        if status.state == BatteryState.DISCHARGING:
            if status.percent > 0.75:
                char = " "
            elif status.percent > 0.45:
                char = " "
            else:
                char = " "
        elif status.percent >= 1 or status.state == BatteryState.FULL:
            char = " "
        elif status.state == BatteryState.EMPTY or status.percent == 0:
            char = " "
        else:
            char = " "
        return self.format.format(char=char, percent=status.percent)

    def restore(self):
        """Restore."""
        self.format = "{char}"
        self.font = widget_defaults.font
        self.timer_setup()

    def button_press(self, x, y, button):
        """Button press."""
        self.format = "{percent:2.0%}"
        self.font = widget_defaults.font
        self.timer_setup()
        self.timeout_add(1, self.restore)


battery = MyBattery(
    format="{char}",
    low_foreground=colors["red"],
    show_short_text=False,
    low_percentage=0.12,
    foreground=colors["white"],
    notify_below=12,
)


def get_widgets():
    return [
        widget.CurrentLayoutIcon(scale=0.8),
        widget.GroupBox(
            highlight_method="block",
            rounded=False,
            this_current_screen_border=colors["blue"],
            other_screen_border=colors["dark_yellow"],
            hide_unused=True,
        ),
        widget.Chord(
            chords_colors={
                "launch": (colors["red"], colors["white"]),
            },
            name_transform=lambda name: name.upper(),
        ),
        widget.Prompt(),
        widget.Spacer(length=10),
        widget.TaskList(
            highlight_method="block",
            border=colors["special_grey"],
            unfocused_border="#353940",
            foreground=colors["white"],
            icon_size=0,
            margin=0,
            title_width_method="uniform",
            # max_title_width=350,
            txt_minimized="絛 ",
            txt_maximized="类 ",
            txt_floating="缾 ",
            parse_text=my_tasklist_parse,
            markup_focused='<span foreground="' + colors["blue"] + '" weight="bold">{}</span>',
        ),
        widget.Spacer(length=13),
        widget.Spacer(length=5),
        widget.GenPollText(
            fmt="祥 {}",
            func=lambda: subprocess.check_output(["timetrace", "status", "--format", "{project}"])
            .decode("utf-8")
            .replace("\n", ""),
            update_interval=5,
            mouse_callbacks={
                "Button1": lazy.spawn("timetrace start hacon"),
                "Button3": lazy.spawn("timetrace stop"),
            },
        ),
        widget.Clock(format=" %H:%M  %d.%m.%Y"),
    ]


screens = []
monitors = get_monitors()
if monitors is not None:
    for monitor in monitors:
        widgets = get_widgets()

        if monitor["primary"]:
            widgets.insert(-3, widget.Systray())
        if monitor["name"] == "eDP1":
            widgets.insert(-3, battery)

        screens.append(
            Screen(
                bar.Bar(
                    widgets,
                    26,
                    background=colors["black"],
                    margin=2,
                ),
                wallpaper=XDG_CONFIG_HOME + "/qtile/onedark.png",
                wallpaper_mode="fill",
            )
        )

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

floating_layout = layout.Floating(
    **layout_defaults,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(wm_class="arandr"),
        Match(wm_class="Cisco AnyConnect Secure Mobility Client"),
        Match(wm_class="Galculator"),
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(title="Qutebrowser Input"),
    ],
)


@hook.subscribe.startup_once
def autostart():
    """Autostart programs."""
    processes = [
        ["dunst"],
        ["autorandr", "--change"],
        ["xrdb", "-merge", "~/.Xresources"],
        ["synology-drive start"],
    ]

    for p in processes:
        subprocess.Popen(p)


@hook.subscribe.screen_change
def set_screens(event):
    """Set screens."""
    subprocess.run(["autorandr", "--change"])
    qtile.restart()
