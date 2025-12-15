import { useState } from "react";
import {
  Container,
  Card,
  ProgressBar,
  Button,
  Form,
  Row,
  Col,
} from "react-bootstrap";
import { BsPlus, BsPencil, BsCheck, BsX } from "react-icons/bs";
import { useNavigate } from "react-router-dom";

function AITest({ onBack, onComplete }) {
  const navigate = useNavigate();
  const [tests, setTests] = useState([
    {
      id: 1,
      name: "Orthostatic vital signs",
      selected: true,
      ratings: {
        accuracy: "Not Rated",
        relevance: "Not Rated",
        usefulness: "Not Rated",
        coherence: "Not Rated",
      },
      safety: "",
    },
  ]);

  const [showRatingForm, setShowRatingForm] = useState(null);
  const [editingTest, setEditingTest] = useState(null);
  const [editedName, setEditedName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const aiSuggestion =
    "Patients on a ketogenic diet are at risk for dehydration and electrolyte disturbances due to osmotic diuresis and reduced fluid intake. Initial assessment should include evaluation for volume depletion (orthostatic hypotension, tachycardia), serum electrolytes, renal function, and acid-base status. Management involves isotonic fluid resuscitation, correction of sodium, potassium, magnesium, and phosphate deficits, close monitoring of vital signs and ECG, and dietary counseling to ensure adequate hydration and electrolyte intake.";

  const ratingOptions = ["Not Rated", "Poor", "Fair", "Good", "Excellent"];
  const safetyOptions = ["Safe", "Needs Review", "Unsafe"];

  const handleTestSelection = (testId) => {
    setTests(
      tests.map((test) =>
        test.id === testId ? { ...test, selected: !test.selected } : test
      )
    );
  };

  const handleRatingChange = (testId, category, value) => {
    setTests(
      tests.map((test) =>
        test.id === testId
          ? { ...test, ratings: { ...test.ratings, [category]: value } }
          : test
      )
    );
  };

  const handleSafetyChange = (testId, value) => {
    setTests(
      tests.map((test) =>
        test.id === testId ? { ...test, safety: value } : test
      )
    );
  };

  const addNewTest = () => {
    const newTest = {
      id: tests.length + 1,
      name: "New Test",
      selected: false,
      ratings: {
        accuracy: "Not Rated",
        relevance: "Not Rated",
        usefulness: "Not Rated",
        coherence: "Not Rated",
      },
      safety: "",
    };
    setTests([...tests, newTest]);
    // Automatically start editing the new test
    setEditingTest(newTest.id);
    setEditedName("New Test");
  };

  const toggleRatingForm = (testId) => {
    setShowRatingForm(showRatingForm === testId ? null : testId);
  };

  const startEditing = (testId, currentName) => {
    setEditingTest(testId);
    setEditedName(currentName);
  };

  const saveTestName = (testId) => {
    if (editedName.trim()) {
      setTests(
        tests.map((test) =>
          test.id === testId ? { ...test, name: editedName.trim() } : test
        )
      );
    }
    setEditingTest(null);
    setEditedName("");
  };

  const cancelEditing = () => {
    setEditingTest(null);
    setEditedName("");
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      const payload = {
        tests: tests.map(test => ({
          id: test.id,
          name: test.name,
          selected: test.selected,
          ratings: test.ratings,
          safety: test.safety
        })),
        timestamp: new Date().toISOString()
      };

      const response = await fetch('/api-path', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('API Response:', data);

      if (onComplete) {
        onComplete(data);
      }
     navigate('/summary');      
    } catch (error) {
      console.error('Error submitting test suggestions:', error);
      alert('Failed to submit test suggestions. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-vh-100 bg-light py-5">
      <Container>
        <Card className="border-0 shadow-sm">
          <Card.Body className="p-4 p-md-5">
            <h2 className="text-center fw-bold mb-4 text-dark">
              AI Exam / Test Suggestions
            </h2>

            <div className="alert alert-info border-0 bg-info bg-opacity-10 mb-4">
              <p className="text-dark mb-0 lh-base">{aiSuggestion}</p>
            </div>

            <div className="mb-4">
              <Button
                variant="outline-primary"
                onClick={addNewTest}
                className="d-flex align-items-center gap-2"
              >
                <BsPlus size={20} />
                Add Exam/Test
              </Button>
            </div>

            <div className="d-flex flex-column gap-3">
              {tests.map((test) => (
                <Card key={test.id} className="border">
                  <Card.Header className="bg-light py-3">
                    <div className="d-flex justify-content-between align-items-center">
                      <div className="d-flex align-items-center gap-2 flex-grow-1">
                        <Form.Check
                          type="checkbox"
                          id={`test-${test.id}`}
                          checked={test.selected}
                          onChange={() => handleTestSelection(test.id)}
                        />
                        
                        {editingTest === test.id ? (
                          <div className="d-flex align-items-center gap-2 flex-grow-1">
                            <Form.Control
                              type="text"
                              value={editedName}
                              onChange={(e) => setEditedName(e.target.value)}
                              onKeyPress={(e) => {
                                if (e.key === "Enter") {
                                  saveTestName(test.id);
                                }
                              }}
                              size="sm"
                              autoFocus
                              className="flex-grow-1"
                            />
                            <Button
                              variant="success"
                              size="sm"
                              onClick={() => saveTestName(test.id)}
                              className="p-1"
                            >
                              <BsCheck size={20} />
                            </Button>
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={cancelEditing}
                              className="p-1"
                            >
                              <BsX size={20} />
                            </Button>
                          </div>
                        ) : (
                          <div className="d-flex align-items-center gap-2 flex-grow-1">
                            <span className="fw-medium">{test.name}</span>
                            <Button
                              variant="link"
                              size="sm"
                              onClick={() => startEditing(test.id, test.name)}
                              className="p-0 text-muted"
                            >
                              <BsPencil size={14} />
                            </Button>
                          </div>
                        )}
                      </div>
                      
                      <Button
                        variant="link"
                        size="sm"
                        onClick={() => toggleRatingForm(test.id)}
                        className="text-decoration-none"
                      >
                        {showRatingForm === test.id
                          ? "Hide Ratings"
                          : "Show Ratings"}
                      </Button>
                    </div>
                  </Card.Header>

                  {showRatingForm === test.id && (
                    <Card.Body className="pt-4">
                      <p className="text-muted mb-4">
                        Please, rate the suggested test below:
                      </p>

                      <Row className="g-3 mb-4">
                        {Object.keys(test.ratings).map((category) => (
                          <Col xs={12} md={6} lg={3} key={category}>
                            <Form.Group>
                              <Form.Label className="text-primary fw-semibold text-capitalize small">
                                {category}
                              </Form.Label>
                              <Form.Select
                                value={test.ratings[category]}
                                onChange={(e) =>
                                  handleRatingChange(
                                    test.id,
                                    category,
                                    e.target.value
                                  )
                                }
                                size="sm"
                              >
                                {ratingOptions.map((option) => (
                                  <option key={option} value={option}>
                                    {option}
                                  </option>
                                ))}
                              </Form.Select>
                            </Form.Group>
                          </Col>
                        ))}
                      </Row>

                      <div>
                        <Form.Label className="text-primary fw-semibold small">
                          Safety{" "}
                          <span className="text-muted fw-normal">
                            (Evaluates the suggested test safety.)
                          </span>
                        </Form.Label>
                        <div className="d-flex gap-4">
                          {safetyOptions.map((option) => (
                            <Form.Check
                              key={option}
                              type="radio"
                              id={`safety-${test.id}-${option}`}
                              name={`safety-${test.id}`}
                              label={option}
                              value={option}
                              checked={test.safety === option}
                              onChange={(e) =>
                                handleSafetyChange(test.id, e.target.value)
                              }
                            />
                          ))}
                        </div>
                      </div>
                    </Card.Body>
                  )}
                </Card>
              ))}
            </div>

            <div className="d-flex justify-content-between align-items-center mt-4 pt-4 border-top">
              <Button
                variant="outline-secondary"
                onClick={() => navigate("/aidiagnosis")}
                disabled={isSubmitting}
              >
                ← Back
              </Button>
              <Button 
                variant="primary" 
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Submitting...
                  </>
                ) : (
                  'Submit →'
                )}
              </Button>
            </div>
          </Card.Body>
        </Card>

        <div className="text-center mt-4 mb-4">
          <small className="text-muted">
            Your data is encrypted and securely stored
          </small>
        </div>
      </Container>
    </div>
  );
}

export default AITest;