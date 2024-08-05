#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from omegaconf import DictConfig

from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
    SharedStaticTaskState,
)
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__DATA_DIR_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__FORM_CONFIG_NAME
from mephisto.client.cli_form_composer_commands import FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME
from mephisto.data_model.qualification import QUAL_GREATER_EQUAL
from mephisto.generators.form_composer.config_validation.task_data_config import (
    create_extrapolated_config,
)
from mephisto.operations.operator import Operator
from mephisto.tools.building_react_apps import examples
from mephisto.tools.scripts import task_script
from mephisto.utils.qualifications import make_qualification_dict


def _generate_data_json_config():
    """
    Generate extrapolated `task_data.json` config file,
    based on existing form and tokens values config files
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(app_path, FORM_COMPOSER__DATA_DIR_NAME, "dynamic")

    form_config_path = os.path.join(data_path, FORM_COMPOSER__FORM_CONFIG_NAME)
    token_sets_values_config_path = os.path.join(
        data_path,
        FORM_COMPOSER__TOKEN_SETS_VALUES_CONFIG_NAME,
    )
    task_data_config_path = os.path.join(data_path, FORM_COMPOSER__DATA_CONFIG_NAME)

    create_extrapolated_config(
        form_config_path=form_config_path,
        token_sets_values_config_path=token_sets_values_config_path,
        task_data_config_path=task_data_config_path,
        data_path=data_path,
    )


@task_script(default_config_file="dynamic_example_ec2_prolific")
def main(operator: Operator, cfg: DictConfig) -> None:
    examples.build_form_composer_dynamic_ec2_prolific(
        force_rebuild=cfg.mephisto.task.force_rebuild,
        post_install_script=cfg.mephisto.task.post_install_script,
    )

    shared_state = SharedStaticTaskState()

    # Mephisto qualifications
    shared_state.qualifications = [
        make_qualification_dict("sample_qual_name", QUAL_GREATER_EQUAL, 1),
    ]

    # Prolific qualifications
    # Note that we'll prefix names with a customary `web.eligibility.models.` later in the code
    shared_state.prolific_specific_qualifications = [
        {
            "name": "AgeRangeEligibilityRequirement",
            "min_age": 18,
            "max_age": 100,
        },
    ]

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    _generate_data_json_config()
    main()
