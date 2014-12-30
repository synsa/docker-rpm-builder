# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import codecs
import glob
import shutil
import logging
import base64
import tempfile

import click

from drb.spectemplate import DoubleDelimiterTemplate
from drb.which import which
from drb.spawn import sp, SpawnedProcessError
from drb.path import getpath

_HELP = """Builds a binary RPM from .src.rpm file.
    Uses `docker run` under the hood.
    """

_logger = logging.getLogger("drb.commands.srcrpm")

@click.command(help=_HELP)
@click.argument("image", type=click.STRING)
@click.argument("srcrpm", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("target_directory", type=click.Path(file_okay=False, resolve_path=True))
@click.option("--root-image-overrides", nargs=1, type=click.Path(exists=True, file_okay=False, resolve_path=True))
def srcrpm(image, srcrpm, target_directory, root_image_overrides=None):
    _logger.info("Now building {srcrpm} on image {image}", locals())
    if not os.path.exists(target_directory):
        os.mkdir(target_directory)

    dockerexec = which("docker")
    dockerscripts = getpath("drb/dockerscripts")
    srpms_temp = tempfile.mkdtemp("SRPMS")
    shutil.copy(srcrpm, srpms_temp)
    srcrpm_basename = os.path.basename(srcrpm)
    uid = os.getuid()
    gid = os.getgid()

    print locals()
    try:
        sp("{dockerexec} run -v {dockerscripts}:/dockerscripts -v {srpms_temp}:/docker-rpm-build-root/SRPMS -v {target_directory}:/docker-rpm-build-root/RPMS"
           " -w /dockerscripts {image} ./rpmbuild-srcrpm-in-docker.sh {srcrpm_basename} {uid} {gid}", **locals())
    finally:
        shutil.rmtree(srpms_temp)

