/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

describe("Loads static_react_task", () => {
  it("Makes request for agent", () => {
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.visit("/");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Loads correct react elements", () => {
    cy.visit("/");
    cy.get('[data-cy="directions-container"]');
    cy.get('[data-cy="task-data-text"]');
    cy.get('[data-cy="good-button"]');
    cy.get('[data-cy="bad-button"]');
  });
});

describe("Submits static_react_task", () => {
  it("Gets request from pressing good button", () => {
    cy.visit("/");
    cy.intercept({ pathname: "/submit_task" }).as("goodTaskSubmit");
    cy.get('[data-cy="good-button"]').click();
    cy.wait("@goodTaskSubmit").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Shows alert from pressing good button", () => {
    cy.visit("/");
    cy.on("window:alert", (txt) => {
      expect(txt).to.contains(
        "Thank you for your submission.\nYou may close this message to view the next task."
      );
    });
    cy.get('[data-cy="good-button"]').click();
  });

  it("Gets request from pressing bad button", () => {
    cy.visit("/");
    cy.intercept({ pathname: "/submit_task" }).as("badTaskSubmit");
    cy.get('[data-cy="bad-button"]').click();
    cy.wait("@badTaskSubmit").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Shows alert from pressing bad button", () => {
    cy.visit("/");
    cy.on("window:alert", (txt) => {
      expect(txt).to.contains(
        "Thank you for your submission.\nYou may close this message to view the next task."
      );
    });
    cy.get('[data-cy="bad-button"]').click();
  });
});
