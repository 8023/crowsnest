#### crowsnest - A webcam Service for multiple Cams and Stream Services.
####
#### Written by Patrick Gehrsitz aka mryel00 <mryel00.github@gmail.com>
#### Copyright 2025 - till today
#### https://github.com/mainsail-crew/crowsnest
####
#### This File is distributed under GPLv3
####


from __future__ import annotations


import os
from collections.abc import Sequence


from ... import logger, v4l2
from .. import camera




class UVC(camera.Camera[dict[str, dict[str, list[str]]]]):
    def __init__(self, path: str, *args, **kwargs) -> None:
        super().__init__(path, *args, **kwargs)
        self.path_by_path = None
        self.path_by_id = None
        if path.startswith("/dev/video"):
            other = kwargs.get("other", None)
            if other:
                self.path_by_path = other.get("by_path", None)
                self.path_by_id = other.get("by_id", None)
        else:
            self.path = os.path.realpath(path)
            self.path_by_id = path
        self.query_controls = v4l2.ctl.get_query_controls(self.path)


        cur_sec = ""
        for name, qc in self.query_controls.items():
            parsed_qc: dict | None = v4l2.ctl.parse_qc_of_path(self.path, qc)


            if parsed_qc is None:
                continue


            if not parsed_qc:
                cur_sec = name
                continue


            self.control_values[cur_sec][name] = parsed_qc
        self.formats = v4l2.ctl.get_formats(self.path)


    def get_formats_string(self) -> str:
        message = ""
        indent = " " * 8
        for fmt, data in self.formats.items():
            message += f"{fmt}:\n"
            for res, fps_list in data.items():
                message += f"{indent}{res}\n"
                for fps in fps_list:
                    message += f"{indent * 2}{fps}\n"
        return message[:-1]


    def has_mjpg_hw_encoder(self) -> bool:
        return any("Motion-JPEG" in fmt for fmt in self.formats)


    def get_controls_string(self) -> str:
        message = ""
        for section, controls in self.control_values.items():
            if section != "":
                message += f"{section}:\n"
            for control, data in controls.items():
                line = f"{control} ({data['type']})"
                line += max(0, 35 - len(line)) * " " + ":"
                if data["type"] in ("int",):
                    line += f" min={data['min']} max={data['max']} step={data['step']}"
                if "default" in data:
                    line += f" default={data['default']}"
                line += f" value={self.get_current_control_value(control)}"
                if "flags" in data:
                    line += f" flags={data['flags']}"
                message += logger.indentation + line + "\n"
                if "menu" in data:
                    for value, name in data["menu"].items():
                        message += logger.indentation * 2 + f"{value}: {name}\n"
            message += "\n"
        return message[:-1]

