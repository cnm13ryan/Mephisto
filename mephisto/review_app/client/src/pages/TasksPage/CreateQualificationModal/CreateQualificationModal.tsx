/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  NEW_QUALIFICATION_DESCRIPTION_LENGTH,
  NEW_QUALIFICATION_NAME_LENGTH,
} from "consts/review";
import cloneDeep from "lodash/cloneDeep";
import * as React from "react";
import { useEffect } from "react";
import { Button, Col, Form, Modal, Row } from "react-bootstrap";
import "./CreateQualificationModal.css";

const DEFAULT_FORM_STATE: CreateQualificationFormType = {
  description: "",
  name: "",
};

type CreateQualificationModalPropsType = {
  show: boolean;
  setShow: React.Dispatch<React.SetStateAction<boolean>>;
  onSubmit: Function;
  setErrors: Function;
};

function CreateQualificationModal(props: CreateQualificationModalPropsType) {
  const [form, setForm] = React.useState<CreateQualificationFormType>(
    cloneDeep(DEFAULT_FORM_STATE)
  );
  const [formIsValid, setFormIsValid] = React.useState<boolean>(false);

  // Methods

  function onModalClose() {
    props.setShow(!props.show);
  }

  function updateForm(fieldName: string, value: string) {
    setForm({ ...form, [fieldName]: value });
  }

  // Effects

  useEffect(() => {
    if (form.name !== "") {
      setFormIsValid(true);
    } else {
      setFormIsValid(false);
    }
  }, [form]);

  useEffect(() => {
    if (props.show) {
      setForm(cloneDeep(DEFAULT_FORM_STATE));
    }
  }, [props.show]);

  return (
    props.show && (
      <Modal
        className={"create-qualification-modal"}
        show={props.show}
        onHide={onModalClose}
      >
        <Modal.Header closeButton={true}>
          <Modal.Title>Create qualification</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <Form
            className={"create-qualification-form"}
            method={"POST"}
            onSubmit={(e) => {
              e.preventDefault();
            }}
          >
            <Form.Group as={Row} className={`mb-2`} controlId={"name"}>
              <Form.Label>
                <small>Name</small>
              </Form.Label>

              <Col>
                <Form.Control
                  size={"sm"}
                  type={"input"}
                  placeholder={"Name"}
                  value={form.name || ""}
                  maxLength={NEW_QUALIFICATION_NAME_LENGTH}
                  onChange={(e) => updateForm("name", e.target.value)}
                />
              </Col>
            </Form.Group>

            <Form.Group as={Row} className={`mb-2`} controlId={"description"}>
              <Form.Label>
                <small>Description</small>
              </Form.Label>

              <Col>
                <Form.Control
                  size={"sm"}
                  type={"textarea"}
                  placeholder={"Description"}
                  value={form.description || ""}
                  as={"textarea"}
                  rows={3}
                  maxLength={NEW_QUALIFICATION_DESCRIPTION_LENGTH}
                  onChange={(e) => updateForm("description", e.target.value)}
                />
              </Col>
            </Form.Group>
          </Form>
        </Modal.Body>

        <Modal.Footer>
          <div className={"create-qualification-buttons"}>
            <Button
              variant={"outline-secondary"}
              size={"sm"}
              onClick={onModalClose}
            >
              Cancel
            </Button>

            <Button
              variant={"success"}
              size={"sm"}
              disabled={!formIsValid}
              onClick={() => formIsValid && props.onSubmit(form)}
            >
              Create
            </Button>
          </div>
        </Modal.Footer>
      </Modal>
    )
  );
}

export default CreateQualificationModal;