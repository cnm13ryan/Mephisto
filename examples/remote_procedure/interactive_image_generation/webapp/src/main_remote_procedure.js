/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import "bootstrap-select/dist/css/bootstrap-select.min.css";
import "bootstrap/dist/css/bootstrap.css";
import "./app_remote_procedure.jsx";
import "./css/style.css";

// To import custom styles added by users in `insertions` directory
// we search for all CSS files in that directory and import them dynamically during webpack build
function importAll(r) {
  r.keys().forEach(r);
}

const cssInsertions = require.context(
  process.env.WEBAPP__GENERATOR__INSERTIONS_DIR,
  true,
  /\.css$/i
);
importAll(cssInsertions);