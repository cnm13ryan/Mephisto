---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 1
---

# Mephisto Task Addons

## Overview

The `mephisto-task-addons` package provides:
- `WorkerOpinion` widget: collect workers' feedback for each completed unit

## Usage

1. Add `mephisto-task-addons` library to your webpack config:
```js
// Specifies location of your packages (e.g. `../../dir`)
var PATH_TO_PACKAGES = "<path>"

module.exports = {
  ...
  resolve: {
    alias: {
      ...
      "mephisto-task-addons": path.resolve(
        __dirname,
        `${PATH_TO_PACKAGES}/packages/mephisto-task-addons`
      ),
    }
  }
};
```

2. Import desired widgets from `mephisto-task-addons` in your code like so:

```jsx
import { WorkerOpinion } from "mephisto-task-addons";
...
<WorkerOpinion
  maxTextLength={500}
  questions={[
    "Was this task hard?",
    "Is this a good example?",
  ]}
/>
```