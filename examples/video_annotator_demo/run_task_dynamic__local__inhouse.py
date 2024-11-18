#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from omegaconf import DictConfig

from mephisto.client.cli_video_annotator_commands import set_video_annotator_env_vars
from mephisto.client.cli_video_annotator_commands import VIDEO_ANNOTATOR__DATA_CONFIG_NAME
from mephisto.client.cli_video_annotator_commands import VIDEO_ANNOTATOR__DATA_DIR_NAME
from mephisto.client.cli_video_annotator_commands import (
    VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME,
)
from mephisto.client.cli_video_annotator_commands import VIDEO_ANNOTATOR__UNIT_CONFIG_NAME
from mephisto.generators.generators_utils.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


def _generate_task_data_json_config():
    """
    Generate extrapolated `task_data.json` config file,
    based on existing form and tokens values config files
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(app_path, VIDEO_ANNOTATOR__DATA_DIR_NAME, "dynamic")

    unit_config_path = os.path.join(data_path, VIDEO_ANNOTATOR__UNIT_CONFIG_NAME)
    token_sets_values_config_path = os.path.join(
        data_path,
        VIDEO_ANNOTATOR__TOKEN_SETS_VALUES_CONFIG_NAME,
    )
    task_data_config_path = os.path.join(data_path, VIDEO_ANNOTATOR__DATA_CONFIG_NAME)

    set_video_annotator_env_vars()

    create_extrapolated_config(
        unit_config_path=unit_config_path,
        token_sets_values_config_path=token_sets_values_config_path,
        task_data_config_path=task_data_config_path,
        data_path=data_path,
    )


@task_script(default_config_file="dynamic_example__local__inhouse")
def main(operator: Operator, cfg: DictConfig) -> None:
    examples.build_video_annotator_dynamic(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )
    operator.launch_task_run(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    _generate_task_data_json_config()
    main()
