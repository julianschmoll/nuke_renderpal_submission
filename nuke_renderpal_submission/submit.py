import os
import logging
import subprocess
from string import Template
from pathlib import Path

import nuke

from nuke_renderpal_submission import update_paths as nuke_paths

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Render Submission")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
LOGGER.addHandler(ch)


def submit_render(dry_run=False):
    scene_path = os.path.normpath(nuke.root().knob('name').value())
    nice_name = assemble_render_set_name(scene_path)
    project_name, shot, version, user = nice_name.split("_")
    cmd = assemble_cmd(
        nice_name,
        create_import_set(scene_path),
        scene_path
    )

    LOGGER.info(f"Submitting to Renderpal with: \n{cmd}")
    print(f"Submitting to Renderpal with: \n{cmd}")

    if dry_run:
        return

    nuke.scriptSave()
    run_wake_up_bats()
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    streamdata = child.communicate()[0]
    rc = child.returncode

    ffmpeg_rset = assemble_ffmpeg_rset(shot, version)
    ffmpeg_cmd = assemble_ffmpeg_cmd(f"CONVERT_{nice_name}", ffmpeg_rset, rc)
    # subprocess.Popen(ffmpeg_cmd)

    nuke.message(f"Submitted {nice_name} ({rc})")


def assemble_render_set_name(scene_path):
    path_elem = scene_path.split(os.sep)
    naming_elem = path_elem[-1].split("_")
    nice_name = "_".join(
        ["Frogging-Comp", path_elem[4], naming_elem[-4], naming_elem[-2]]
    )
    return nice_name


def assemble_cmd(render_name, import_set, scene_path, chunk_size=100):
    return " ".join(
        [
            f'"{get_renderpal_exe()}"',
            '-login="ca-user:polytopixel"',
            '-nj_renderer="Nuke/Frog Nuke"',
            f'-nj_splitmode="2,{chunk_size}"',
            "-retnjid",
            f'-nj_name="{render_name}"',
            '-nj_project="Frogging Hell"',
            f'-importset="{import_set}"',
            f'"{scene_path}"'
        ]
    )


def assemble_ffmpeg_cmd(render_name, import_set, dep_id):
    return " ".join(
        [
            f'"{get_renderpal_exe()}"',
            '-login="ca-user:polytopixel"',
            '-nj_renderer="Frog FFmpeg/Default version"',
            "-retnjid",
            f"-nj_dependency {dep_id}",
            "-nj_deptype 0",
            f'-nj_name="{render_name}"',
            '-nj_project="Frogging Hell"',
            f'-importset="{import_set}"',
            "FFMPEG"
        ]
    )


def create_import_set(scene_path):
    parent_path = os.path.dirname(scene_path)
    content = """
    <RenderSet>
        <Values>
            <frames>
                <Value>{0}-{1}</Value>
            </frames>
        </Values>
    </RenderSet>
    """.format(*get_frame_ramge())
    r_set_file = os.path.join(parent_path, "renderpal.rset")

    with open(r_set_file, "w") as r_set:
        r_set.write(content)

    return r_set_file


def get_frame_ramge():
    return nuke.Root()["first_frame"].getValue(), nuke.Root()["last_frame"].getValue()


def run_wake_up_bats():
    LOGGER.info("Waking up computers :)")
    subprocess.Popen(
        "K:/wake_042.bat", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    subprocess.Popen(
        "K:/wake_043.bat", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )


def assemble_ffmpeg_rset(shot, version):
    root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    search_path = nuke_paths.assemble_render_path().replace("####", "%04d")
    parent_path = os.path.dirname(nuke.root().knob("name").value())
    file = os.path.join(root_dir, "resources", "ffmpeg_rset_template.txt")

    d = {
        "input": search_path.replace(os.sep, "/"),
        "out_dir":os.path.dirname(search_path).replace(os.sep, "/"),
        "out_file": f"Shot_{shot}_{version}_qc_render.mp4",
        "start_frame": int(nuke.Root()['first_frame'].value())
    }

    with open(file, "r") as f:
        src = Template(f.read())
        result = src.substitute(d)

    r_set_file = os.path.join(
        parent_path, f"ffmpeg_render_set_{version}.rnjprs"
    )

    with open(r_set_file, "w") as r_set:
        r_set.write(result)

    return r_set_file


def get_renderpal_exe():
    return "C:\Program Files (x86)\RenderPal V2\CmdRC\RpRcCmd.exe"
