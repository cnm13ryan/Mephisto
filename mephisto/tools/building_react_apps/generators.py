#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional

from mephisto.generators.form_composer.config_validation.utils import set_custom_triggers_js_env_var
from mephisto.generators.form_composer.config_validation.utils import (
    set_custom_validators_js_env_var,
)
from mephisto.tools.scripts import build_custom_bundle
from mephisto.utils.console_writer import ConsoleWriter
from . import packages
from .utils import clean_single_react_app

REPO_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
FORM_COMPOSER_GENERATOR_PATH = os.path.join(REPO_PATH, "mephisto", "generators", "form_composer")

logger = ConsoleWriter()


# --- CLEAN ---


def clean_form_composer_generator(remove_package_locks: bool, verbose: bool = False):
    webapp_path = os.path.join(FORM_COMPOSER_GENERATOR_PATH, "webapp")
    clean_single_react_app(webapp_path, remove_package_locks=remove_package_locks, verbose=verbose)


# --- BUILD ---


def build_form_composer_generator(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
    verbose: bool = False,
):
    if verbose:
        logger.info(f"[blue]Building '{FORM_COMPOSER_GENERATOR_PATH}'[/blue]")

    # Set env var for `custom_validators.js`
    from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_DIR_NAME

    data_path = os.path.join(FORM_COMPOSER_GENERATOR_PATH, FORM_COMPOSER__DATA_DIR_NAME)
    set_custom_validators_js_env_var(data_path)
    set_custom_triggers_js_env_var(data_path)

    # Build Review UI for the application
    build_custom_bundle(
        FORM_COMPOSER_GENERATOR_PATH,
        force_rebuild=force_rebuild,
        webapp_name="webapp",
        build_command="build:review",
    )

    # Build Task UI for the application
    build_custom_bundle(
        FORM_COMPOSER_GENERATOR_PATH,
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        webapp_name="webapp",
        build_command="build",
    )


def build_form_composer_generator_with_packages(
    force_rebuild: bool = False,
    post_install_script: Optional[str] = None,
    verbose: bool = False,
) -> None:
    packages.build_mephisto_task_multipart_package(force_rebuild=force_rebuild, verbose=verbose)
    packages.build_react_form_composer_package(force_rebuild=force_rebuild, verbose=verbose)
    build_form_composer_generator(
        force_rebuild=force_rebuild,
        post_install_script=post_install_script,
        verbose=verbose,
    )