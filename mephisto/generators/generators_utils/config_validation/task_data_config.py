#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os.path
import re
from copy import deepcopy
from typing import List
from typing import Optional
from typing import Tuple

from mephisto.generators.generators_utils.constants import S3_URL_EXPIRATION_MINUTES_MAX
from mephisto.generators.generators_utils.constants import TOKEN_END_REGEX
from mephisto.generators.generators_utils.constants import TOKEN_START_REGEX
from mephisto.generators.generators_utils.remote_procedures import ProcedureName
from mephisto.utils.console_writer import ConsoleWriter
from .common_validation import replace_path_to_file_with_its_content
from .config_validation_constants import TOKENS_VALUES_KEY
from .separate_token_values_config import validate_separate_token_values_config
from .token_sets_values_config import validate_token_sets_values_config
from .utils import get_s3_presigned_url
from .utils import get_validation_mappings
from .utils import make_error_message
from .utils import read_config_file
from .utils import write_config_to_file

logger = ConsoleWriter()


def _extrapolate_tokens_values(
    text: str,
    tokens_values: dict,
    data_path: Optional[str] = None,
    token_start_regex: Optional[str] = TOKEN_START_REGEX,
    token_end_regex: Optional[str] = TOKEN_END_REGEX,
) -> str:
    for token, value in tokens_values.items():
        # For HTML paths
        value = replace_path_to_file_with_its_content(value, data_path)

        # For other values
        text = re.sub(
            (
                token_start_regex
                + r"(\s*)"
                +
                # Escape and add regexp grouping parentheses around the token
                # (in case it has special characters)
                r"("
                + re.escape(token)
                + r")"
                + "(\s*)"
                + token_end_regex
            ),
            str(value),
            text,
        )
    return text


def set_tokens_in_unit_config_item(
    item: dict,
    tokens_values: dict,
    data_path: Optional[str] = None,
    token_start_regex: Optional[str] = TOKEN_START_REGEX,
    token_end_regex: Optional[str] = TOKEN_END_REGEX,
):
    attrs_supporting_tokens = get_validation_mappings()["ATTRS_SUPPORTING_TOKENS"]
    for attr_name in attrs_supporting_tokens:
        item_attr = item.get(attr_name)
        if not item_attr:
            continue

        item[attr_name] = _extrapolate_tokens_values(
            text=item_attr,
            tokens_values=tokens_values,
            data_path=data_path,
            token_start_regex=token_start_regex,
            token_end_regex=token_end_regex,
        )


def _collect_tokens_from_unit_config(
    config_data: dict,
    regex: Optional[str] = None,
) -> Tuple[set, List[str]]:
    regex = regex or r"\s*(\w+?)\s*"

    validation_mappings = get_validation_mappings()
    attrs_supporting_tokens = validation_mappings["ATTRS_SUPPORTING_TOKENS"]
    _collect_unit_config_items_to_extrapolate = validation_mappings[
        "collect_unit_config_items_to_extrapolate"
    ]

    items_to_extrapolate = _collect_unit_config_items_to_extrapolate(config_data)
    tokens_in_unit_config = set()
    tokens_in_unexpected_attrs_errors = []

    for item in items_to_extrapolate:
        for attr_name in attrs_supporting_tokens:
            item_attr = item.get(attr_name)
            if not item_attr:
                continue

            tokens_in_unit_config.update(
                set(
                    re.findall(
                        TOKEN_START_REGEX + regex + TOKEN_END_REGEX,
                        item_attr,
                    )
                )
            )

        attrs_not_suppoting_tokens = set(item.keys()) - set(attrs_supporting_tokens)
        for attr_name in attrs_not_suppoting_tokens:
            item_attr = item.get(attr_name)
            if isinstance(item_attr, str):
                found_attr_tokens = re.findall(
                    TOKEN_START_REGEX + regex + TOKEN_END_REGEX,
                    item_attr,
                )
                if found_attr_tokens:
                    found_attr_tokens_string = ", ".join([f"'{t}'" for t in found_attr_tokens])
                    tokens_in_unexpected_attrs_errors.append(
                        f"You tried to set tokens {found_attr_tokens_string} "
                        f"in attribute '{attr_name}' with value '{item_attr}'. "
                        f"You can use tokens only in following attributes: "
                        f"{', '.join(attrs_supporting_tokens)}"
                    )

    return tokens_in_unit_config, tokens_in_unexpected_attrs_errors


def _extrapolate_tokens_in_unit_config(
    config_data: dict,
    tokens_values: dict,
    data_path: Optional[str] = None,
) -> dict:
    _collect_unit_config_items_to_extrapolate = get_validation_mappings()[
        "collect_unit_config_items_to_extrapolate"
    ]
    items_to_extrapolate = _collect_unit_config_items_to_extrapolate(config_data)
    for item in items_to_extrapolate:
        set_tokens_in_unit_config_item(item, tokens_values, data_path)

    return config_data


def _validate_tokens_in_both_configs(
    unit_config_data: dict,
    token_sets_values_config_data: List[dict],
) -> Tuple[set, set, list]:
    tokens_from_unit_config, tokens_in_unexpected_attrs_errors = _collect_tokens_from_unit_config(
        unit_config_data
    )
    tokens_from_token_sets_values_config = set(
        [
            token_name
            for token_set_values_data in token_sets_values_config_data
            for token_name in token_set_values_data.get(TOKENS_VALUES_KEY, {}).keys()
        ]
    )
    # Token names present in token values config, but not in form config
    overspecified_tokens = tokens_from_token_sets_values_config - tokens_from_unit_config
    # Token names present in form config, but not in token values config
    underspecified_tokens = tokens_from_unit_config - tokens_from_token_sets_values_config
    return overspecified_tokens, underspecified_tokens, tokens_in_unexpected_attrs_errors


def _combine_extrapolated_unit_configs(
    unit_config_data: dict,
    token_sets_values_config_data: List[dict],
    data_path: Optional[str] = None,
) -> List[dict]:
    validation_mappings = get_validation_mappings()
    generator_metadata_key = validation_mappings["GENERATOR_METADATA_KEY"]
    _validate_unit_config_func = validation_mappings["validate_unit_config"]

    errors = []

    # Validate Unit config
    unit_config_is_valid, unit_config_errors = _validate_unit_config_func(unit_config_data)

    if not unit_config_is_valid:
        # Stop generating a Task, the config is incorrect
        raise ValueError("\n" + "\n\n".join(unit_config_errors))

    (
        token_sets_values_config_is_valid,
        token_sets_values_data_config_errors,
    ) = validate_token_sets_values_config(token_sets_values_config_data)

    # Validate that same token names are present in both configs
    (
        overspecified_tokens,
        underspecified_tokens,
        tokens_in_unexpected_attrs_errors,
    ) = _validate_tokens_in_both_configs(
        unit_config_data,
        token_sets_values_config_data,
    )

    # Output errors, if any
    if overspecified_tokens:
        errors.append(
            f"Values for the following tokens are provided in token sets values config, "
            f"but they are not defined in the form config: "
            f"{', '.join(overspecified_tokens)}."
        )
    if underspecified_tokens:
        errors.append(
            f"The following tokens are specified in the form config, "
            f"but their values are not provided in the token sets values config: "
            f"{', '.join(underspecified_tokens)}."
        )

    if tokens_in_unexpected_attrs_errors:
        errors = errors + tokens_in_unexpected_attrs_errors

    if not unit_config_is_valid:
        errors.append(make_error_message("Unit config is invalid", unit_config_errors))

    if not token_sets_values_config_is_valid:
        errors.append(
            make_error_message(
                "Token sets values config is invalid",
                token_sets_values_data_config_errors,
            )
        )

    if errors:
        # Stop generating a Task, the config is incorrect
        raise ValueError("\n" + "\n\n".join(errors))

    # If no errors, combine extrapolated form versions to create Task data config
    combined_config = []
    if token_sets_values_config_data:
        for token_sets_values in token_sets_values_config_data:
            if token_sets_values == {}:
                combined_config.append(unit_config_data)
            else:
                unit_config_data_with_tokens = _extrapolate_tokens_in_unit_config(
                    deepcopy(unit_config_data),
                    token_sets_values[TOKENS_VALUES_KEY],
                    data_path=data_path,
                )

                # Add token values into metadata
                prev_metadata = unit_config_data_with_tokens.get(generator_metadata_key, {})
                prev_metadata.update(token_sets_values)
                unit_config_data_with_tokens[generator_metadata_key] = prev_metadata

                combined_config.append(unit_config_data_with_tokens)
    else:
        # If no config with tokens values was added than
        # we just create one-unit config and copy form config into it as-is
        combined_config.append(unit_config_data)

    return combined_config


def _replace_html_paths_with_html_file_content(
    config_data: dict,
    data_path: str,
) -> dict:
    validation_mappings = get_validation_mappings()
    attrs_supporting_tokens = validation_mappings["ATTRS_SUPPORTING_TOKENS"]
    _collect_unit_config_items_to_extrapolate = validation_mappings[
        "collect_unit_config_items_to_extrapolate"
    ]

    items_to_replace = _collect_unit_config_items_to_extrapolate(config_data)

    for item in items_to_replace:
        for attr_name in attrs_supporting_tokens:
            item_attr = item.get(attr_name)
            if not item_attr:
                continue

            item[attr_name] = replace_path_to_file_with_its_content(item_attr, data_path)

    return config_data


def create_extrapolated_config(
    unit_config_path: str,
    token_sets_values_config_path: str,
    task_data_config_path: str,
    data_path: Optional[str] = None,
):
    # Ensure form config file exists
    if not os.path.exists(unit_config_path):
        raise FileNotFoundError(f"Create file '{unit_config_path}' with form configuration.")

    # Read JSON from files
    unit_config_data = read_config_file(unit_config_path)

    # Handle HTML insertion files (replace their paths with file content)
    if data_path:
        unit_config_data = _replace_html_paths_with_html_file_content(
            unit_config_data,
            data_path,
        )

    # Get token sets values
    if os.path.exists(token_sets_values_config_path):
        token_sets_values_data = read_config_file(token_sets_values_config_path)
    else:
        token_sets_values_data = []

    # Create Task data config (with multiple form versions)
    try:
        extrapolated_unit_config_data = _combine_extrapolated_unit_configs(
            unit_config_data,
            token_sets_values_data,
            data_path,
        )
        write_config_to_file(extrapolated_unit_config_data, task_data_config_path)
    except (ValueError, FileNotFoundError) as e:
        logger.info(f"\n[red]Could not extrapolate form configs:[/red] {e}\n")
        exit()


def validate_task_data_config(config_data: List[dict]) -> Tuple[bool, List[str]]:
    is_valid = True
    errors = []

    if not isinstance(config_data, list):
        is_valid = False
        errors.append("Config must be a JSON Array.")

    if config_data:
        if not all(config_data):
            is_valid = False
            errors.append("Task data config must contain at least one non-empty item.")

        # Validate each form version contained in task data config
        for item in config_data:
            _validate_unit_config_func = get_validation_mappings()["validate_unit_config"]
            unit_config_is_valid, unit_config_errors = _validate_unit_config_func(item)
            if not unit_config_is_valid:
                is_valid = False
                errors += unit_config_errors

    return is_valid, errors


def verify_generator_configs(
    task_data_config_path: str,
    unit_config_path: Optional[str] = None,
    token_sets_values_config_path: Optional[str] = None,
    separate_token_values_config_path: Optional[str] = None,
    task_data_config_only: bool = False,
    data_path: Optional[str] = None,
    force_exit: bool = False,
    error_message: Optional[str] = None,
):
    error_message = (
        error_message or "\n[red]Provided Form Composer config files are invalid:[/red] {exc}\n"
    )
    errors = []

    try:
        # 1. Validate task data config
        task_data_config_data = read_config_file(task_data_config_path, exit_if_no_file=False)

        if task_data_config_data is None:
            pass
        else:
            task_data_config_is_valid, task_data_config_errors = validate_task_data_config(
                task_data_config_data,
            )
            if not task_data_config_is_valid:
                errors.append(
                    make_error_message(
                        "Task data config is invalid",
                        task_data_config_errors,
                    )
                )

        if task_data_config_only:
            if errors:
                raise ValueError(make_error_message("", errors))

            return None

        # 2. Validate form config
        unit_config_data = read_config_file(unit_config_path, exit_if_no_file=False)

        if unit_config_data is None:
            pass
        else:
            # Handle HTML insertion files (replace their paths with file content)
            if data_path:
                unit_config_data = _replace_html_paths_with_html_file_content(
                    unit_config_data,
                    data_path,
                )

            _validate_unit_config_func = get_validation_mappings()["validate_unit_config"]
            unit_config_is_valid, unit_config_errors = _validate_unit_config_func(
                unit_config_data,
                data_path,
            )

            if not unit_config_is_valid:
                errors.append(make_error_message("Unit config is invalid", unit_config_errors))

        # 3. Validate token sets values config
        token_sets_values_data = read_config_file(
            token_sets_values_config_path,
            exit_if_no_file=False,
        )

        # 3a. Validate token sets values data itself
        if token_sets_values_data is None:
            token_sets_values_data = []
        else:
            (
                token_sets_values_config_is_valid,
                token_sets_values_config_errors,
            ) = validate_token_sets_values_config(token_sets_values_data)

            if not token_sets_values_config_is_valid:
                errors.append(
                    make_error_message(
                        "Token sets values config is invalid",
                        token_sets_values_config_errors,
                        indent=4,
                    )
                )

        # 3b. Ensure there's no unused token names in both token setes and form config
        (
            overspecified_tokens,
            underspecified_tokens,
            tokens_in_unexpected_attrs_errors,
        ) = _validate_tokens_in_both_configs(unit_config_data, token_sets_values_data)

        if overspecified_tokens:
            errors.append(
                f"Values for the following tokens are provided in token sets values config, "
                f"but they are not defined in the form config: "
                f"{', '.join(overspecified_tokens)}."
            )
        if underspecified_tokens:
            errors.append(
                f"The following tokens are specified in the form config, "
                f"but their values are not provided in the token sets values config: "
                f"{', '.join(underspecified_tokens)}."
            )

        if tokens_in_unexpected_attrs_errors:
            errors = errors + tokens_in_unexpected_attrs_errors

        # 4. Validate separate token values config
        separate_token_values_config_data = read_config_file(
            separate_token_values_config_path,
            exit_if_no_file=False,
        )

        (
            separate_token_values_config_is_valid,
            separate_token_values_config_errors,
        ) = validate_separate_token_values_config(separate_token_values_config_data)

        if not separate_token_values_config_is_valid:
            errors.append(
                make_error_message(
                    "Separate token values config is invalid",
                    separate_token_values_config_errors,
                )
            )

        if errors:
            raise ValueError(make_error_message("", errors))
        else:
            logger.info(f"[green]All configs are valid.[/green]")

    except ValueError as e:
        logger.info(error_message.format(exc=e))

        if force_exit:
            exit()


def prepare_task_config_for_review_app(config_data: dict) -> dict:
    config_data = deepcopy(config_data)

    procedure_code_regex = r"\s*(.+?)\s*"
    tokens_from_inputs, _ = _collect_tokens_from_unit_config(
        config_data,
        regex=procedure_code_regex,
    )

    url_from_rpocedure_code_regex = r"\(\"(.+?)\"\)"
    token_values = {}
    for token in tokens_from_inputs:
        presigned_url_procedure_names = [
            ProcedureName.GET_MULTIPLE_PRESIGNED_URLS,
            ProcedureName.GET_PRESIGNED_URL,
        ]
        if any([p in token for p in presigned_url_procedure_names]):
            url = re.findall(url_from_rpocedure_code_regex, token)[0]
            # Presign URL for max possible perioid of time,
            # because there's no need to hide files from researchers
            # and review can last for a long time
            presigned_url = get_s3_presigned_url(url, S3_URL_EXPIRATION_MINUTES_MAX)
            token_values[token] = presigned_url

    prepared_config = _extrapolate_tokens_in_unit_config(config_data, token_values)
    return prepared_config
