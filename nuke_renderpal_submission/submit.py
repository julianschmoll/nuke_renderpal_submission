import os
import logging
import subprocess

import nuke

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Render Submission")


def submit_render(dry_run=False):
    scene_path = os.path.normpath(nuke.root().knob('name').value())
    cmd = assemble_cmd(
        assemble_render_set_name(scene_path),
        create_import_set(scene_path),
        scene_path
    )

    LOGGER.info(f"Submitting to Renderpal with: \n{cmd}")

    if dry_run:
        return

    nuke.scriptSave()
    run_wake_up_bats()
    subprocess.Popen(cmd)


def assemble_render_set_name(scene_path):
    path_elem = scene_path.split(os.sep)
    naming_elem = path_elem[-1].split("_")
    nice_name = "_".join(
        ["Frogging-Comp", path_elem[4], naming_elem[-4], naming_elem[-2]]
    )
    return nice_name


def assemble_cmd(render_name, import_set, scene_path, chunk_size=15):
    return " ".join(
        [
            f'"{get_renderpal_exe()}"',
            '-login="ca-user:polytopixel" '
            '-nj_renderer="Nuke/Frog Nuke"',
            f'-nj_splitmode="2,{chunk_size}"',
            f'-nj_name="{render_name}"',
            '-nj_project="Frogging Hell"',
            f'-importset="{import_set}"',
            f'"{scene_path}"'
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


def get_renderpal_exe():
    return "C:\Program Files (x86)\RenderPal V2\CmdRC\RpRcCmd.exe"
