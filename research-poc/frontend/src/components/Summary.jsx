import React, { useState } from "react";
import { Container, Button } from "react-bootstrap";
import { BsX, BsCheck } from "react-icons/bs";
import { useNavigate } from "react-router-dom";

function Summary() {
  const navigate = useNavigate();

  const [summaryText] = useState(
    "For suspected urinary tract infection (UTI), initial evaluation focuses on confirming infection and identifying the causative organism to guide therapy. A urinalysis with dipstick and microscopic examination helps detect pyuria and bacteriuria; a urine culture and sensitivity test identifies the pathogen and its antibiotic susceptibilities. In uncomplicated cases, these are usually sufficient. Additional blood tests and imaging studies are reserved for complicated, recurrent, or atypical presentations, or when obstruction or anatomic abnormalities are suspected."
  );

  const [diagnoses] = useState([
    {
      id: 1,
      name: "Dehydration and electrolyte imbalance secondary to ketogenic diet",
      selected: false,
      accuracy: null,
      relevance: null,
      usefulness: null,
      coherence: null,
      comments: null
    },
    {
      id: 2,
      name: "Urinary tract infection",
      selected: true,
      accuracy: "10",
      relevance: "10",
      usefulness: "10",
      coherence: "10",
      comments: "none"
    },
    {
      id: 3,
      name: "Benign prostatic hyperplasia",
      selected: false,
      accuracy: null,
      relevance: null,
      usefulness: null,
      coherence: null,
      comments: null
    },
    {
      id: 4,
      name: "Neurogenic bladder from a neurological disorder (e.g., multiple sclerosis or spinal cord lesion)",
      selected: false,
      accuracy: null,
      relevance: null,
      usefulness: null,
      coherence: null,
      comments: null
    },
    {
      id: 5,
      name: "Diabetic ketoacidosis or uncontrolled diabetes mellitus",
      selected: false,
      accuracy: null,
      relevance: null,
      usefulness: null,
      coherence: null,
      comments: null
    }
  ]);

  return (
    <div className="min-vh-100 bg-white py-5">
      <Container className="px-4 px-md-5">
        <div className="mb-5">
          <h2 className="fw-bold mb-2">Summary</h2>
          <p className="text-muted small mb-3 pb-3 border-bottom">
            The summary of the patient's condition is based on the selected diagnosis
          </p>
          <p className="text-dark lh-lg" style={{ fontSize: '15px' }}>
            {summaryText}
          </p>
        </div>

        <div className="mb-5">
          <h2 className="fw-bold mb-2 mt-5">Evaluation</h2>
          <p className="text-muted small mb-4 pb-3 border-bottom">
            The evaluations for the ai suggested diagnoses
          </p>

          <div className="table-responsive">
            <table className="table table-borderless" style={{ fontSize: '15px' }}>
              <thead>
                <tr className="bg-primary bg-opacity-10">
                  <th className="fw-semibold text-dark py-3 ps-3" style={{ width: '100px' }}>Selected</th>
                  <th className="fw-semibold text-dark py-3">Diagnosis</th>
                  <th className="fw-semibold text-dark py-3 text-end pe-4" style={{ width: '120px' }}>Accuracy</th>
                  <th className="fw-semibold text-dark py-3 text-end pe-4" style={{ width: '120px' }}>Relevance</th>
                  <th className="fw-semibold text-dark py-3 text-end pe-4" style={{ width: '130px' }}>Usefulness</th>
                  <th className="fw-semibold text-dark py-3 text-end pe-4" style={{ width: '130px' }}>Coherence</th>
                  <th className="fw-semibold text-dark py-3 text-end pe-4" style={{ width: '130px' }}>Comments</th>
                </tr>
              </thead>
              <tbody>
                {diagnoses.map((diagnosis, index) => (
                  <tr
                    key={diagnosis.id}
                    className={diagnosis.selected ? "bg-success bg-opacity-10" : index % 2 === 1 ? "bg-light" : ""}
                    style={{ borderBottom: '1px solid #dee2e6' }}
                  >
                    <td className="align-middle py-3 ps-3">
                      <div className="d-flex justify-content-center">
                        {diagnosis.selected ? (
                          <div className="border border-success rounded d-flex align-items-center justify-content-center" 
                               style={{ width: '24px', height: '24px', backgroundColor: '#d1e7dd' }}>
                            <BsCheck size={20} className="text-success" strokeWidth={1} />
                          </div>
                        ) : (
                          <BsX size={24} className="text-muted" />
                        )}
                      </div>
                    </td>
                    <td className="align-middle py-3 text-dark">
                      {diagnosis.name}
                    </td>
                    <td className="align-middle py-3 text-end pe-4 text-dark">
                      {diagnosis.accuracy || ""}
                    </td>
                    <td className="align-middle py-3 text-end pe-4 text-dark">
                      {diagnosis.relevance || ""}
                    </td>
                    <td className="align-middle py-3 text-end pe-4 text-dark">
                      {diagnosis.usefulness || ""}
                    </td>
                    <td className="align-middle py-3 text-end pe-4 text-dark">
                      {diagnosis.coherence || ""}
                    </td>
                    <td className="align-middle py-3 text-end pe-4 text-dark">
                      {diagnosis.comments || ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="d-flex justify-content-between align-items-center mt-5">
          <Button
            variant="outline-secondary"
            onClick={() => navigate("/aitest")}
            className="px-4"
          >
            ← Back
          </Button>
          <Button
            variant="primary"
            onClick={() => navigate("/")}
            className="px-4"
          >
            Finish
          </Button>
        </div>
      </Container>
    </div>
  );
}

export default Summary;