import React, { useState } from "react";
import {
  Form,
  Button,
  Container,
  Card,
  ProgressBar,
  Row,
  Col,
} from "react-bootstrap";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import {
  FaBolt,
  FaWalking,
  FaHeartbeat,
  FaBicycle,
  FaUser,
} from "react-icons/fa";
import { BsSmartwatch } from "react-icons/bs";
import { useNavigate } from "react-router-dom";

export default function StepThree() {
  const { t } = useTranslation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const [showUpload, setShowUpload] = useState(false);
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const onSubmit = () => {
    const patientId = localStorage.getItem('currentPatientId');
    if (showUpload) {
      if (!file) {
        alert('Please select a file to upload');
        return;
      }
      if (!patientId) {
        alert('No active patient found. Please start with Add Patient.');
        return;
      }
      import('../api').then(({ api }) => {
        const fd = new FormData();
        fd.append('file', file);
        fetch(api(`/api/v1/patients/${patientId}/wearable/upload`), {
          method: 'POST',
          body: fd,
        })
          .then(async (res) => {
            if (!res.ok) throw new Error(await res.text());
            const j = await res.json();
            console.log('✅ Wearable data uploaded:', j);
            alert('Wearable data uploaded successfully!');
            // clear current patient id after completing flow
            localStorage.removeItem('currentPatientId');
            navigate('/');
          })
          .catch((err) => {
            console.error(err);
            alert('Failed to upload wearable: ' + err.message);
          });
      });
    } else {
      // skip upload -> finish flow
      localStorage.removeItem('currentPatientId');
      navigate('/');
      console.log('⏭ Skipped wearable data upload');
    }
  };

  return (
    <div className="bg-light min-vh-100 py-5">
      <Container>
        <div className="mb-4">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <small className="text-muted fw-semibold">Step 3 of 4</small>
            <small className="text-muted">75% Complete</small>
          </div>
          <ProgressBar now={75} style={{ height: "8px" }} className="mb-3" />
        </div>

        <Card className="border-0 shadow-sm">
          <Card.Body className="p-4 p-md-5">
            {!showUpload ? (
              <>
                <div className="text-center">
                  <div className="mb-4">
                    <h2 className="fw-bold text-primary mb-2">
                      {t("wearable.title")}
                    </h2>
                    <p className="text-muted mb-1">
                      {t("wearable.description")}
                    </p>
                  </div>

                  <div className="my-0 py-0">
                    <Row className="g-2 justify-content-center">
                      <Col xs={4} sm={2}>
                        <div className="p-3 bg-primary bg-opacity-10 rounded-3 d-inline-flex">
                          <BsSmartwatch
                            className="text-primary"
                            style={{ fontSize: "1.75rem" }}
                          />
                        </div>
                      </Col>
                      <Col xs={4} sm={2}>
                        <div className="p-3 bg-warning bg-opacity-10 rounded-3 d-inline-flex">
                          <FaBolt
                            className="text-warning"
                            style={{ fontSize: "1.75rem" }}
                          />
                        </div>
                      </Col>
                      <Col xs={4} sm={2}>
                        <div className="p-3 bg-success bg-opacity-10 rounded-3 d-inline-flex">
                          <FaWalking
                            className="text-success"
                            style={{ fontSize: "1.75rem" }}
                          />
                        </div>
                      </Col>
                      <Col xs={4} sm={2}>
                        <div className="p-3 bg-danger bg-opacity-10 rounded-3 d-inline-flex">
                          <FaHeartbeat
                            className="text-danger"
                            style={{ fontSize: "1.75rem" }}
                          />
                        </div>
                      </Col>
                      <Col xs={4} sm={2}>
                        <div className="p-3 bg-info bg-opacity-10 rounded-3 d-inline-flex">
                          <FaBicycle
                            className="text-info"
                            style={{ fontSize: "1.75rem" }}
                          />
                        </div>
                      </Col>
                      <Col xs={4} sm={2}>
                        <div className="p-3 bg-secondary bg-opacity-10 rounded-3 d-inline-flex">
                          <FaUser
                            className="text-secondary"
                            style={{ fontSize: "1.75rem" }}
                          />
                        </div>
                      </Col>
                    </Row>
                  </div>
                  <div className="my-4">
                    <h5 className="fw-semibold mb-4">
                      {t("wearable.question")}
                    </h5>

                    <div className="alert alert-info border-0 bg-info bg-opacity-10 mb-4 text-start">
                      <div className="d-flex align-items-start">
                        <span className="me-2">💡</span>
                        <small className="text-muted">
                          Wearable data helps us provide more accurate health
                          insights and personalized recommendations.
                        </small>
                      </div>
                    </div>
                  </div>

                  <div className="d-flex flex-column flex-sm-row justify-content-center gap-3 mt-4">
                    <Button
                      variant="primary"
                      size="md"
                      // className="px-5 py-3"
                      onClick={() => setShowUpload(true)}
                    >
                      <BsSmartwatch className="me-2" />
                      {t("wearable.yes")}
                    </Button>
                    <Button
                      variant="outline-secondary"
                      size="md"
                      // className="px-5 py-3"
                      onClick={handleSubmit(onSubmit)}
                    >
                      {t("wearable.no")} - Skip for now
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div>
                  <div className="mb-4">
                    <h2 className="fw-bold text-primary mb-2">
                      {t("wearable.title")}
                    </h2>
                    <p className="text-muted mb-0">
                      {t("wearable.uploadInstruction")}
                    </p>
                  </div>

                  <Form onSubmit={handleSubmit(onSubmit)}>
                    <div className="my-5">
                      <div className="border-2 border-dashed rounded-3 p-5 text-center bg-light">
                        <div className="mb-3">
                          <BsSmartwatch
                            className="text-primary"
                            style={{ fontSize: "3rem" }}
                          />
                        </div>

                        <Form.Group className="mb-3">
                          <Form.Control
                            type="file"
                            accept=".csv,.json"
                            size="lg"
                            className={`${
                              errors.wearableFile ? "is-invalid" : ""
                            }`}
                            {...register("wearableFile", {
                              required: "Please select a file to upload",
                            })}
                            onChange={(e) => setFile(e.target.files[0])}
                          />
                          {errors.wearableFile && (
                            <Form.Control.Feedback
                              type="invalid"
                              className="d-block"
                            >
                              {errors.wearableFile.message}
                            </Form.Control.Feedback>
                          )}
                        </Form.Group>

                        <small className="text-muted">
                          Supported formats: CSV, JSON
                        </small>

                        {file && (
                          <div className="mt-3 p-3 bg-success bg-opacity-10 rounded-2">
                            <small className="text-success fw-semibold">
                              ✓ Selected: {file.name}
                            </small>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="alert alert-warning border-0 bg-warning bg-opacity-10 mb-4">
                      <div className="d-flex align-items-start">
                        <span className="me-2">⚠️</span>
                        <small className="text-muted">
                          Make sure your file contains valid wearable device
                          data in CSV or JSON format.
                        </small>
                      </div>
                    </div>

                    <div className="d-flex justify-content-between align-items-center pt-3">
                      <Button
                        variant="outline-secondary"
                        size="md"
                        // className="px-4 py-2"
                        onClick={() => setShowUpload(false)}
                      >
                        ← {t("wearable.back")}
                      </Button>
                      <Button
                        type="submit"
                        variant="primary"
                        size="md"
                        // className="px-5 py-3"
                      >
                        {t("wearable.upload")} →
                      </Button>
                    </div>
                  </Form>
                </div>
              </>
            )}
          </Card.Body>
        </Card>

        <div className="text-center mt-4">
          <small className="text-muted">
            Your data is encrypted and securely stored
          </small>
        </div>
      </Container>
    </div>
  );
}
