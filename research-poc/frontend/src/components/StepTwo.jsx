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
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

export default function StepTwo() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const onSubmit = (data) => {
    // send lifestyle to backend for current patient
    const patientId = localStorage.getItem('currentPatientId');
    if (!patientId) {
      alert('No active patient found. Please start with Add Patient.');
      return;
    }
    import('../api').then(({ api }) => {
      fetch(api(`/api/v1/patients/${patientId}/lifestyle`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          diet: data.diet,
          sleep_hours: data.sleep,
          exercise: data.exercise,
          mental_activities: data.mental,
        }),
      })
        .then(async (res) => {
          if (!res.ok) throw new Error(await res.text());
          alert('Form submitted successfully!');
          navigate('/wearable');
        })
        .catch((err) => {
          console.error(err);
          alert('Failed to save lifestyle: ' + err.message);
        });
    });
  };

  return (
    <div className="bg-light min-vh-100 py-5">
      <Container>
        <div className="mb-4">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <small className="text-muted fw-semibold">Step 2 of 4</small>
            <small className="text-muted">50% Complete</small>
          </div>
          <ProgressBar now={50} style={{ height: "8px" }} className="mb-3" />
        </div>

        <Card className="border-0 shadow-sm">
          <Card.Body className="p-4 p-md-5">
            <Form onSubmit={handleSubmit(onSubmit)}>
              <div className="mb-5">
                <div className="mb-4">
                  <h2 className="fw-bold text-primary mb-2">
                    {t("lifestyle.title")}
                  </h2>
                  <p className="text-muted mb-0">
                    Tell us about your daily habits and routines
                  </p>
                </div>

                <Row className="g-4">
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label className="fw-semibold mb-2">
                        {t("lifestyle.diet")}{" "}
                        <span className="text-danger">*</span>
                      </Form.Label>
                      <Form.Control
                        className={`py-3 ${errors.diet ? "is-invalid" : ""}`}
                        placeholder="e.g. balanced, keto, vegetarian"
                        {...register("diet", {
                          required: "Diet pattern is required",
                        })}
                      />
                      {errors.diet && (
                        <Form.Control.Feedback
                          type="invalid"
                          className="d-block"
                        >
                          {errors.diet.message}
                        </Form.Control.Feedback>
                      )}
                    </Form.Group>
                  </Col>

                  <Col md={6}>
                    <Form.Group>
                      <Form.Label className="fw-semibold mb-2">
                        {t("lifestyle.sleep")}{" "}
                        <span className="text-danger">*</span>
                      </Form.Label>
                      <div className="input-group">
                        <Form.Control
                          type="number"
                          step="0.5"
                          className={`py-3 ${errors.sleep ? "is-invalid" : ""}`}
                          placeholder="Enter hours"
                          {...register("sleep", {
                            required: "Sleep duration is required",
                            min: {
                              value: 1,
                              message: "Sleep must be at least 1 hour",
                            },
                            max: {
                              value: 24,
                              message: "Sleep cannot exceed 24 hours",
                            },
                          })}
                        />
                        <span className="input-group-text bg-light">
                          hours/night
                        </span>
                        {errors.sleep && (
                          <Form.Control.Feedback
                            type="invalid"
                            className="d-block"
                          >
                            {errors.sleep.message}
                          </Form.Control.Feedback>
                        )}
                      </div>
                    </Form.Group>
                  </Col>
                </Row>

                <Row className="g-4 mt-2">
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label className="fw-semibold mb-2">
                        {t("lifestyle.exercise")}{" "}
                        <span className="text-danger">*</span>
                      </Form.Label>
                      <Form.Control
                        className={`py-3 ${
                          errors.exercise ? "is-invalid" : ""
                        }`}
                        placeholder="e.g. running 3x/week, gym daily"
                        {...register("exercise", {
                          required: "Exercise info is required",
                        })}
                      />
                      {errors.exercise && (
                        <Form.Control.Feedback
                          type="invalid"
                          className="d-block"
                        >
                          {errors.exercise.message}
                        </Form.Control.Feedback>
                      )}
                    </Form.Group>
                  </Col>

                  <Col md={6}>
                    <Form.Group>
                      <Form.Label className="fw-semibold mb-2">
                        {t("lifestyle.mental")}{" "}
                        <span className="text-danger">*</span>
                      </Form.Label>
                      <Form.Control
                        className={`py-3 ${errors.mental ? "is-invalid" : ""}`}
                        placeholder="e.g. meditation, reading, yoga"
                        {...register("mental", {
                          required: "Mental activity is required",
                        })}
                      />
                      {errors.mental && (
                        <Form.Control.Feedback
                          type="invalid"
                          className="d-block"
                        >
                          {errors.mental.message}
                        </Form.Control.Feedback>
                      )}
                    </Form.Group>
                  </Col>
                </Row>
              </div>

              <hr className="my-5" />

              <div className="mb-5">
                <div className="mb-4">
                  <h2 className="fw-bold text-primary mb-2">
                    {t("symptoms.title")}
                  </h2>
                  <p className="text-muted mb-0">
                    Describe any current symptoms or concerns
                  </p>
                </div>

                <Form.Group>
                  <Form.Label className="fw-semibold mb-2">
                    {t("symptoms.describe")}{" "}
                    <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    className={`${errors.symptoms ? "is-invalid" : ""}`}
                    placeholder={t("symptoms.placeholder")}
                    style={{ resize: "vertical" }}
                    {...register("symptoms", {
                      required: "Please describe your symptoms",
                      minLength: {
                        value: 10,
                        message:
                          "Please provide more details (at least 10 characters)",
                      },
                    })}
                  />
                  {errors.symptoms && (
                    <Form.Control.Feedback type="invalid" className="d-block">
                      {errors.symptoms.message}
                    </Form.Control.Feedback>
                  )}
                  <Form.Text className="text-muted">
                    Be as specific as possible about when symptoms occur and
                    their severity
                  </Form.Text>
                </Form.Group>
              </div>

              <hr className="my-5" />

              <div className="mb-5">
                <div className="mb-4">
                  <h2 className="fw-bold text-primary mb-2">
                    {t("mentalhealth.title")}
                  </h2>
                  <p className="text-muted mb-0">
                    Share any mental health concerns or stress factors
                  </p>
                </div>

                <Form.Group>
                  <Form.Label className="fw-semibold mb-2">
                    {t("mentalhealth.label")}{" "}
                    <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    className={`${errors.mentalHealth ? "is-invalid" : ""}`}
                    placeholder="e.g. stress levels, anxiety, mood changes, sleep quality concerns"
                    style={{ resize: "vertical" }}
                    {...register("mentalHealth", {
                      required: "Please share any mental health concerns",
                      minLength: {
                        value: 10,
                        message:
                          "Please provide more details (at least 10 characters)",
                      },
                    })}
                  />
                  {errors.mentalHealth && (
                    <Form.Control.Feedback type="invalid" className="d-block">
                      {errors.mentalHealth.message}
                    </Form.Control.Feedback>
                  )}
                </Form.Group>

                <div className="alert alert-info border-0 bg-info bg-opacity-10 mt-3">
                  <div className="d-flex align-items-start">
                    <span className="me-2">🔒</span>
                    <small className="text-muted">
                      All mental health information is confidential and used
                      only for providing appropriate care
                    </small>
                  </div>
                </div>
              </div>

              <hr className="my-5" />

              <div className="mb-5">
                <div className="mb-4">
                  <h2 className="fw-bold text-primary mb-2">
                    {t("exams.title")}
                  </h2>
                  <p className="text-muted mb-0">
                    List any previous medical tests or examinations
                  </p>
                </div>

                <Form.Group>
                  <Form.Label className="fw-semibold mb-2">
                    {t("exams.label")} <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    className={`${errors.previousExams ? "is-invalid" : ""}`}
                    placeholder="e.g. blood tests (date), X-rays, MRI scans, etc."
                    style={{ resize: "vertical" }}
                    {...register("previousExams", {
                      required: "Please list previous exams or write 'None'",
                      minLength: {
                        value: 4,
                        message: "Please provide more details or write 'None'",
                      },
                    })}
                  />
                  {errors.previousExams && (
                    <Form.Control.Feedback type="invalid" className="d-block">
                      {errors.previousExams.message}
                    </Form.Control.Feedback>
                  )}
                  <Form.Text className="text-muted">
                    Include dates and results if available, or write "None" if
                    no previous exams
                  </Form.Text>
                </Form.Group>
              </div>

              <div className="d-flex justify-content-between align-items-center pt-3 border-top">
                <Button
                  variant="outline-secondary"
                  onClick={() => navigate(-1)}
                  size="md"
                  // className="px-4 py-2"
                >
                  ← Back
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  // className="px-5 py-3"
                >
                  {t("lifestyle.next")} →
                </Button>
              </div>
            </Form>
          </Card.Body>
        </Card>

        <div className="text-center mt-4">
          <small className="text-muted">
            All information is kept confidential and secure
          </small>
        </div>
      </Container>
    </div>
  );
}
