/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { DEFAULT_COLLAPSABLE, DEFAULT_INITIALLY_COLLAPSED } from "./constants";
import "./Section.css";
import { SectionErrors } from "./SectionErrors.jsx";
import { SectionErrorsCountBadge } from "./SectionErrorsCountBadge.jsx";
import { runCustomTrigger } from "./utils";

function Section({
  children,
  customTriggers,
  data,
  formFields,
  formState,
  formatStringWithTokens,
  inReviewState,
  index,
  invalidFormFields,
  remoteProcedureCollection,
  sectionsFields,
  setRenderingErrors,
  updateFormData,
}) {
  const title = formatStringWithTokens(data.title, setRenderingErrors);
  const instruction = formatStringWithTokens(
    data.instruction,
    setRenderingErrors
  );

  const collapsable = [null, undefined].includes(data.collapsable) // Not specified in config
    ? DEFAULT_COLLAPSABLE
    : data.collapsable;
  const initiallyCollapsed = collapsable
    ? [null, undefined].includes(data.initially_collapsed) // Not specified in config
      ? DEFAULT_INITIALLY_COLLAPSED
      : data.initially_collapsed
    : false;

  const hasInvalidFields = !!(sectionsFields[index] || []).filter((field) =>
    Object.keys(invalidFormFields).includes(field.name)
  ).length;

  function onClickSectionHeader() {
    if (inReviewState) {
      return;
    }

    runCustomTrigger({
      elementTriggersConfig: data.triggers,
      elementTriggerName: "onClick",
      customTriggers: customTriggers,
      formData: formState,
      updateFormData: updateFormData,
      element: data,
      fieldValue: null,
      formFields: formFields,
      remoteProcedureCollection: remoteProcedureCollection,
    });
  }

  return (
    <section
      className={`section ${data.classes || ""}`}
      id={data.id}
      data-id={`section-${index}`}
      data-invalid={hasInvalidFields}
    >
      {(title || instruction) && (
        // Section header is clickable for accordion
        <div
          className={`
            section-header
            alert
            alert-info
            ${collapsable ? "collapsable" : ""}
            ${hasInvalidFields ? "has-invalid-fields" : ""}
          `}
          role={"alert"}
          id={`accordion_heading_${index}`}
          onClick={onClickSectionHeader}
          data-toggle={collapsable ? "collapse" : null}
          data-target={
            collapsable ? `#accordion_collapsable_part_${index}` : null
          }
          aria-expanded={collapsable ? initiallyCollapsed : null}
          aria-controls={
            collapsable ? `accordion_collapsable_part_${index}` : null
          }
        >
          <div className="row justify-content-between">
            {/* Section name on the left side */}
            {title && (
              <h4
                className={`
                  col-8
                  section-name
                  ${collapsable ? "dropdown-toggle" : ""}
                `}
                dangerouslySetInnerHTML={{ __html: title }}
              ></h4>
            )}

            {/* Badge with errors number on the right side */}
            <div className={`col-1`}>
              <SectionErrorsCountBadge
                sectionFields={sectionsFields[index]}
                invalidFormFields={invalidFormFields}
              />
            </div>
          </div>

          {title && instruction && <hr />}

          {instruction && (
            <p
              className={`section-instruction`}
              dangerouslySetInnerHTML={{ __html: instruction }}
            ></p>
          )}
        </div>
      )}

      {/* Collapsable part of section with fieldsets */}
      <div
        id={`accordion_collapsable_part_${index}`}
        className={`
          collapse
          ${collapsable ? "" : "non-collapsable"}
          ${initiallyCollapsed ? "" : "show"}
        `}
        aria-labelledby={`accordion_heading_${index}`}
        data-parent={`#id_accordion`}
      >
        <SectionErrors
          sectionFields={sectionsFields[index]}
          invalidFormFields={invalidFormFields}
        />

        {/* Fieldsets */}
        {children}
      </div>
    </section>
  );
}

export { Section };