/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import "./FieldSet.css";

function FieldSet({
  children,
  data,
  formatStringWithTokens,
  setRenderingErrors,
}) {
  const title = formatStringWithTokens(data.title, setRenderingErrors);
  const instruction = formatStringWithTokens(
    data.instruction,
    setRenderingErrors
  );

  return (
    <fieldset
      className={`fieldset container ${data.classes || ""}`}
      id={data.id}
    >
      {title || instruction ? (
        <div className={`fieldset-header alert alert-secondary`} role={"alert"}>
          {title && (
            <h5
              className={`fieldset-name`}
              dangerouslySetInnerHTML={{
                __html: title,
              }}
            ></h5>
          )}

          {title && instruction && <hr />}

          {instruction && (
            <p
              className={`fieldset-instruction`}
              dangerouslySetInnerHTML={{
                __html: instruction,
              }}
            ></p>
          )}
        </div>
      ) : (
        <hr />
      )}

      {/* Rows */}
      {children}
    </fieldset>
  );
}

export { FieldSet };