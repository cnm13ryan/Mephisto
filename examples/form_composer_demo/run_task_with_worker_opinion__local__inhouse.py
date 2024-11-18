#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from omegaconf import DictConfig

from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script


@task_script(default_config_file="example__local__inhouse")
def main(operator: Operator, cfg: DictConfig) -> None:
    os.environ["REACT_APP__WITH_WORKER_OPINION"] = "true"
    examples.build_form_composer_simple(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )
    operator.launch_task_run(cfg.mephisto)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
