import React, { useState } from "react";
import {
  Container,
  Card,
  Button,
  Form,
  Row,
  Col,
  Modal,
} from "react-bootstrap";
import { BsPlus, BsX } from "react-icons/bs";
import { useNavigate } from "react-router-dom";

function AIDiagnosis({ onBack }) {
  const navigate = useNavigate();
  const [diagnoses, setDiagnoses] = useState([
    {
      id: 1,
      name: "Dehydration and electrolyte imbalance from ketogenic diet",
      selected: false,
    },
    { id: 2, name: "Keto flu (dietary adaptation symptoms)", selected: false },
    {
      id: 3,
      name: "Tension-type headache related to stress and inactivity",
      selected: false,
    },
    { id: 4, name: "Migraine headache", selected: false },
    { id: 5, name: "Hypoglycemia", selected: false },
  ]);

  const [showAddModal, setShowAddModal] = useState(false);
  const [newDiagnosis, setNewDiagnosis] = useState("");
  const [expandedDiagnosis, setExpandedDiagnosis] = useState(null);
  const [ratings, setRatings] = useState({});
  const [comments, setComments] = useState({});

  const caseDescription =
    "A 25-year-old woman on a ketogenic diet with no regular exercise presents with headache and nausea in the context of stress and anxiety. Her presentation raises concern for diet-related metabolic changes and tension-type headache as well as possible migraine triggers.";

  const handleAddDiagnosis = () => {
    if (newDiagnosis.trim()) {
      const newDiag = {
        id: diagnoses.length + 1,
        name: newDiagnosis.trim(),
        selected: false,
      };
      setDiagnoses([...diagnoses, newDiag]);
      setNewDiagnosis("");
      setShowAddModal(false);
    }
  };

  const toggleDiagnosisExpansion = (diagId) => {
    setExpandedDiagnosis(expandedDiagnosis === diagId ? null : diagId);
  };

  const toggleSelection = (diagId) => {
    setDiagnoses(
      diagnoses.map((d) =>
        d.id === diagId ? { ...d, selected: !d.selected } : d
      )
    );
  };

  const handleRatingChange = (diagId, category, value) => {
    setRatings({
      ...ratings,
      [diagId]: {
        ...(ratings[diagId] || {}),
        [category]: value,
      },
    });
  };

  const handleCommentChange = (diagId, value) => {
    setComments({
      ...comments,
      [diagId]: value,
    });
  };

  const getRating = (diagId, category) => {
    return ratings[diagId]?.[category] || "10";
  };

  return (
    <div className="min-vh-100 bg-light py-5">
      <Container>
        <Card className="border-0 shadow-sm mb-4">
          <Card.Body className="p-4 p-md-5">
            <h2 className="fw-bold mb-4 text-dark">
              AI Differential Diagnosis
            </h2>

            <div className="alert alert-info border-0 bg-info bg-opacity-10 mb-4">
              <p className="text-dark mb-0 lh-base">{caseDescription}</p>
            </div>

            <div className="mb-4">
              <Button
                variant="outline-primary"
                onClick={() => setShowAddModal(true)}
                className="d-flex align-items-center gap-2"
              >
                <BsPlus size={20} />
                Add Diagnosis
              </Button>
            </div>

            <div className="d-flex flex-column gap-3 mb-4">
              {diagnoses.map((diagnosis) => (
                <Card key={diagnosis.id} className="border">
                  <Card.Header
                    className="bg-light py-3 cursor-pointer"
                    style={{ cursor: "pointer" }}
                    onClick={() => toggleDiagnosisExpansion(diagnosis.id)}
                  >
                    <div className="d-flex align-items-center gap-3">
                      <Form.Check
                        type="checkbox"
                        id={`diagnosis-${diagnosis.id}`}
                        checked={diagnosis.selected}
                        onChange={(e) => {
                          e.stopPropagation();
                          toggleSelection(diagnosis.id);
                        }}
                        className="me-2"
                      />
                      <span className="text-dark">{diagnosis.name}</span>
                    </div>
                  </Card.Header>

                  {expandedDiagnosis === diagnosis.id && (
                    <Card.Body className="pt-4 bg-white">
                      <p className="text-muted mb-4">
                        Please, rate the suggested diagnosis below:
                      </p>

                      <Row className="g-3 mb-4">
                        <Col xs={12} sm={6} md={3}>
                          <Form.Group>
                            <Form.Label className="text-primary fw-semibold small">
                              Accuracy
                            </Form.Label>
                            <Form.Select
                              value={getRating(diagnosis.id, "accuracy")}
                              onChange={(e) =>
                                handleRatingChange(
                                  diagnosis.id,
                                  "accuracy",
                                  e.target.value
                                )
                              }
                              size="sm"
                            >
                              {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((num) => (
                                <option key={num} value={num}>
                                  {num}
                                </option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                        </Col>

                        <Col xs={12} sm={6} md={3}>
                          <Form.Group>
                            <Form.Label className="text-primary fw-semibold small">
                              Relevance
                            </Form.Label>
                            <Form.Select
                              value={getRating(diagnosis.id, "relevance")}
                              onChange={(e) =>
                                handleRatingChange(
                                  diagnosis.id,
                                  "relevance",
                                  e.target.value
                                )
                              }
                              size="sm"
                            >
                              {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((num) => (
                                <option key={num} value={num}>
                                  {num}
                                </option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                        </Col>

                        <Col xs={12} sm={6} md={3}>
                          <Form.Group>
                            <Form.Label className="text-primary fw-semibold small">
                              Usefulness
                            </Form.Label>
                            <Form.Select
                              value={getRating(diagnosis.id, "usefulness")}
                              onChange={(e) =>
                                handleRatingChange(
                                  diagnosis.id,
                                  "usefulness",
                                  e.target.value
                                )
                              }
                              size="sm"
                            >
                              {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((num) => (
                                <option key={num} value={num}>
                                  {num}
                                </option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                        </Col>

                        <Col xs={12} sm={6} md={3}>
                          <Form.Group>
                            <Form.Label className="text-primary fw-semibold small">
                              Coherence
                            </Form.Label>
                            <Form.Select
                              value={getRating(diagnosis.id, "coherence")}
                              onChange={(e) =>
                                handleRatingChange(
                                  diagnosis.id,
                                  "coherence",
                                  e.target.value
                                )
                              }
                              size="sm"
                            >
                              {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((num) => (
                                <option key={num} value={num}>
                                  {num}
                                </option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                        </Col>
                      </Row>

                      <div>
                        <Form.Label className="text-primary fw-semibold small">
                          Comments
                        </Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={4}
                          value={comments[diagnosis.id] || ""}
                          onChange={(e) =>
                            handleCommentChange(diagnosis.id, e.target.value)
                          }
                          placeholder="Add any observations about the suggested diagnosis"
                          className="border-primary border-2"
                          style={{ resize: "none" }}
                        />
                      </div>
                    </Card.Body>
                  )}
                </Card>
              ))}
            </div>

            <div className="mt-4">
              <Button
                variant="primary"
                onClick={() => navigate("/aitest")}
                className="px-4"
              >
                Next
              </Button>
            </div>
          </Card.Body>
        </Card>
      </Container>

      <Modal
        show={showAddModal}
        onHide={() => setShowAddModal(false)}
        centered
        size="lg"
      >
        <Modal.Header className="border-0 pb-0">
          <Modal.Title className="fw-bold">Add Diagnosis</Modal.Title>
          <Button
            variant="link"
            className="text-muted p-0"
            onClick={() => setShowAddModal(false)}
          >
            <BsX size={32} />
          </Button>
        </Modal.Header>

        <Modal.Body className="pt-3">
          <p className="text-muted mb-4">
            The model generates diagnostic suggestions based on the given input
            data. However, these outputs may not encompass all clinically
            plausible hypotheses. To improve diagnostic coverage, users may
            manually insert additional candidate conditions supported by their
            clinical evaluation.
          </p>

          <Form.Group className="mb-4">
            <Form.Label className="fw-semibold">Diagnosis</Form.Label>
            <Form.Control
              type="text"
              value={newDiagnosis}
              onChange={(e) => setNewDiagnosis(e.target.value)}
              placeholder="Enter diagnosis name"
              className="border-primary border-2"
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleAddDiagnosis();
                }
              }}
              autoFocus
            />
          </Form.Group>

          <div className="d-flex justify-content-end gap-3">
            <Button
              variant="outline-secondary"
              onClick={() => setShowAddModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="success"
              onClick={handleAddDiagnosis}
              disabled={!newDiagnosis.trim()}
            >
              Add Diagnosis
            </Button>
          </div>
        </Modal.Body>
      </Modal>
    </div>
  );
}

export default AIDiagnosis;
