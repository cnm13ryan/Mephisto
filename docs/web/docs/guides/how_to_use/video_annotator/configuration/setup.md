---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 5
---

# VideoAnnotator configuration

VideoAnnotator tasks are fully defined by their configuration files. These files comprise:
- The main JSON file `task_data.json` that specifies all fields across all annotator versions (their visual layout, validators, etc)
- Auxiliary JSON files (such as `token_sets_values_config.json`) that specifies certain parts of the main config (e.g. only variable parts varing between annotator versions). The main JSON file is construvted out of these by using `mephisto form_composer` CLI command.
- Custom pieces of code specified in a special `insertions` subdirectory, such as HTML content of lengthy annotator instructions.

The structure and purpose of these files is detailed further in other sections:
- [Config files reference](/docs/guides/how_to_use/video_annotator/configuration/config_files/)
- [Using multiple annotator versions](/docs/guides/how_to_use/video_annotator/configuration/multiple_annotator_versions/)
- [`video_annotator config` command](/docs/guides/how_to_use/video_annotator/configuration/video_annotator_config_command/)
- [Using code insertions](/docs/guides/how_to_use/video_annotator/configuration/insertions/)
- [Form rendering callbacks](/docs/guides/how_to_use/video_annotator/configuration/form_callbacks/)


To test the effect of configuration changes on a finished Task, you can use working VideoAnnotator examples in the `examples/video_annotator_demo/data` directory.