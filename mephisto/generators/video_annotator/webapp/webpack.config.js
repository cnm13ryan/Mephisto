/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: "./src/main.js",
  output: {
    path: __dirname,
    filename: "build/bundle.js",
  },
  resolve: {
    alias: {
      react: path.resolve("./node_modules/react"),
      // Use local library with code that can submit FormData
      "mephisto-task-multipart": path.resolve(
        __dirname,
        "../../../../packages/mephisto-task-multipart"
      ),
      // Use local library with code that can use FormComposer and  submit Worker Opinion
      "mephisto-task-addons": path.resolve(
        __dirname,
        "../../../../packages/mephisto-task-addons"
      ),
      // Required for custom validators
      "custom-validators": path.resolve(
        process.env.WEBAPP__GENERATOR__CUSTOM_VALIDATORS
      ),
      // Required for custom triggers
      "custom-triggers": path.resolve(
        process.env.WEBAPP__GENERATOR__CUSTOM_TRIGGERS
      ),
    },
    fallback: {
      net: false,
      dns: false,
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/i,
        loader: "babel-loader",
        exclude: /node_modules/,
        options: { presets: ["@babel/env"] },
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
};