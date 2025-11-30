import React from "react";
import { useForm } from "react-hook-form";
import {
  Form,
  Button,
  Container,
  Row,
  Col,
  Card,
  ProgressBar,
} from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function StepOne() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const onSubmit = (data) => {
    // Create patient with demographics (backend) and store current patient id
    import('../api').then(({ api }) => {
      fetch(api('/api/v1/patients'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          age: data.age,
          gender: data.gender,
          weight: data.weight,
          height: data.height,
        }),
      })
        .then(async (res) => {
          if (!res.ok) {
            const text = await res.text();
            throw new Error(text || 'Failed to create patient');
          }
          return res.json();
        })
        .then((json) => {
          // save id and continue
          localStorage.setItem('currentPatientId', json.id);
          navigate('/lifestyle');
        })
        .catch((err) => {
          console.error(err);
          alert('Failed to create patient: ' + err.message);
        });
    });
  };

  return (
    <div className="bg-light min-vh-100 py-5">
      <Container>
        <div className="mb-4">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <small className="text-muted fw-semibold">Step 1 of 4</small>
            <small className="text-muted">25% Complete</small>
          </div>
          <ProgressBar now={25} style={{ height: "8px" }} className="mb-3" />
        </div>

        <Card className="border-0 shadow-sm">
          <Card.Body className="p-4 p-md-5">
            <div className="mb-4">
              <h2 className="fw-bold text-primary mb-2">
                {t("demographics.title")}
              </h2>
              <p className="text-muted mb-0">
                Please provide basic demographic information
              </p>
            </div>

            <Form onSubmit={handleSubmit(onSubmit)}>
              <Row className="g-4 mb-4">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label className="fw-semibold mb-2">
                      {t("demographics.age")}{" "}
                      <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Control
                      type="number"
                      placeholder="Enter age"
                      className={`py-3 ${errors.age ? "is-invalid" : ""}`}
                      {...register("age", {
                        required: t("validation.ageRequired"),
                        min: {
                          value: 1,
                          message: "Age must be greater than 0",
                        },
                        max: {
                          value: 120,
                          message: "Please enter a valid age",
                        },
                      })}
                    />
                    {errors.age && (
                      <Form.Control.Feedback type="invalid" className="d-block">
                        {errors.age.message}
                      </Form.Control.Feedback>
                    )}
                  </Form.Group>
                </Col>

                <Col md={6}>
                  <Form.Group>
                    <Form.Label className="fw-semibold mb-2">
                      {t("demographics.gender")}{" "}
                      <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Select
                      className={`py-3 ${errors.gender ? "is-invalid" : ""}`}
                      {...register("gender", {
                        required: t("validation.genderRequired"),
                      })}
                    >
                      <option value="">Select gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                      <option value="prefer-not-to-say">
                        Prefer not to say
                      </option>
                    </Form.Select>
                    {errors.gender && (
                      <Form.Control.Feedback type="invalid" className="d-block">
                        {errors.gender.message}
                      </Form.Control.Feedback>
                    )}
                  </Form.Group>
                </Col>
              </Row>

              <Row className="g-4 mb-4">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label className="fw-semibold mb-2">
                      {t("demographics.weight")}{" "}
                      <span className="text-danger">*</span>
                    </Form.Label>
                    <div className="input-group">
                      <Form.Control
                        type="number"
                        step="0.1"
                        placeholder="Enter weight"
                        className={`py-3 ${errors.weight ? "is-invalid" : ""}`}
                        {...register("weight", {
                          required: t("validation.weightRequired"),
                          min: {
                            value: 1,
                            message: "Weight must be greater than 0",
                          },
                        })}
                      />
                      <span className="input-group-text bg-light">kg</span>
                      {errors.weight && (
                        <Form.Control.Feedback
                          type="invalid"
                          className="d-block"
                        >
                          {errors.weight.message}
                        </Form.Control.Feedback>
                      )}
                    </div>
                  </Form.Group>
                </Col>

                <Col md={6}>
                  <Form.Group>
                    <Form.Label className="fw-semibold mb-2">
                      {t("demographics.height")}{" "}
                      <span className="text-danger">*</span>
                    </Form.Label>
                    <div className="input-group">
                      <Form.Control
                        type="number"
                        step="0.1"
                        placeholder="Enter height"
                        className={`py-3 ${errors.height ? "is-invalid" : ""}`}
                        {...register("height", {
                          required: t("validation.heightRequired"),
                          min: {
                            value: 1,
                            message: "Height must be greater than 0",
                          },
                        })}
                      />
                      <span className="input-group-text bg-light">cm</span>
                      {errors.height && (
                        <Form.Control.Feedback
                          type="invalid"
                          className="d-block"
                        >
                          {errors.height.message}
                        </Form.Control.Feedback>
                      )}
                    </div>
                  </Form.Group>
                </Col>
              </Row>

              <div className="alert alert-info border-0 bg-info bg-opacity-10 mb-4">
                <div className="d-flex align-items-start">
                  <span className="me-2">ℹ️</span>
                  <small className="text-muted">
                    All information is kept confidential and used only for
                    medical assessment purposes.
                  </small>
                </div>
              </div>

              <div className="d-flex justify-content-between align-items-center pt-3">
                <Button
                  variant="outline-secondary"
                  onClick={() => navigate(-1)}
                  size="md"
                >
                  ← Back
                </Button>
                <Button type="submit" variant="primary" size="md">
                  {t("demographics.next")} →
                </Button>
              </div>
            </Form>
          </Card.Body>
        </Card>

        <div className="text-center mt-4">
          <small className="text-muted">
            Need help? Contact support at support@example.com
          </small>
        </div>
      </Container>
    </div>
  );
}
