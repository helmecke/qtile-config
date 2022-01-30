from typing import Dict, List

from Xlib import display


def get_monitors() -> List[Dict[str, bool]]:
    """Get monitors"""

    monitors = []
    d = display.Display()
    res = d.screen().root.xrandr_get_screen_resources()._data
    primary = d.screen().root.xrandr_get_output_primary()._data

    for output in res["outputs"]:
        mon = d.xrandr_get_output_info(output, res["config_timestamp"])._data
        if mon["num_preferred"]:
            if output == primary["output"]:
                monitors.insert(
                    0,
                    {
                        "name": mon["name"],
                        "primary": True,
                    },
                )
            else:
                monitors.append(
                    {
                        "name": mon["name"],
                        "primary": False,
                    }
                )

    return monitors
