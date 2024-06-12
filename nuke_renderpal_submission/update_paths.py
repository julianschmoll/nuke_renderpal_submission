import nuke
import logging
import os


LOGGER = logging.getLogger("Nuke Render")


def assemble_render_path(scene_path=None):
    if not scene_path:
        scene_path = os.path.normpath(nuke.root().knob('name').value())
    path_elem = scene_path.split(os.sep)
    path_elem[0] = "M:\\"
    naming_elem = path_elem[-1].split("_")

    LOGGER.info("Setting Render Paths")
    file_name = "shot_{0}_2d_####.exr".format(naming_elem[1])
    render_path = os.path.join(
        *path_elem[0:5],
        "Rendering",
        "2dRender",
        naming_elem[4],
        file_name
    )
    LOGGER.info(f"Setting render path to {render_path}")

    return render_path


def update_write_nodes():
    updated_nodes = []

    for node in nuke.selectedNodes():
        if node.Class() != "Write":
            continue

        current_path = node.knob("file").value()
        expected_path = assemble_render_path()

        if not current_path == expected_path:
            os.makedirs(os.path.dirname(expected_path), exist_ok=True)
            node.knob("file").setValue(expected_path.replace("\\", "/"))
            updated_nodes.append(node)

    if len(updated_nodes) == 0:
        nuke.message("No nodes were updated")
    else:
        message_string = f"{len(updated_nodes)} nodes were updated:\n\n"
        for node in updated_nodes:
            message_string += f"{node.name()} \n"

        nuke.message(message_string)
