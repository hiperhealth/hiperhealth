import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Container,
  Card,
  Row,
  Col,
  Table,
  Badge,
} from "react-bootstrap";
import { useTranslation } from "react-i18next";
import ReactPaginate from "react-paginate";

export default function Dashboard() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  //   const [patients, setPatients] = useState([]);
  const [patients] = useState([
    {
      id: 1,
      name: "John Doe",
      age: 45,
      gender: "Male",
      status: "Active",
      lastVisit: "2025-10-28",
    },
    {
      id: 2,
      name: "Maria Gonzalez",
      age: 34,
      gender: "Female",
      status: "Under Review",
      lastVisit: "2025-10-15",
    },
    {
      id: 3,
      name: "Arjun Patel",
      age: 29,
      gender: "Male",
      status: "Completed",
      lastVisit: "2025-09-30",
    },
    {
      id: 4,
      name: "Sophia Lee",
      age: 52,
      gender: "Female",
      status: "Active",
      lastVisit: "2025-10-29",
    },
  ]);
  const itemsPerPage = 3;
  const [itemOffset, setItemOffset] = useState(0);

  const endOffset = itemOffset + itemsPerPage;
  const currentItems = patients.slice(itemOffset, endOffset);
  const pageCount = Math.ceil(patients.length / itemsPerPage);

  const handlePageClick = (event) => {
    const newOffset = (event.selected * itemsPerPage) % patients.length;
    setItemOffset(newOffset);
  };
  const hasPatients =patients.length > 0 || 4 ;

  return (
    <div className="bg-light min-vh-100 py-3">
      <Container>
        <div className="mb-2 d-flex justify-content-between align-items-center">
          <div>
            <h1 className="display-7 fw-bold text-primary mb-2">
              {t("dashboard.title")}
            </h1>
            <p className="text-muted lead mb-0">
              Manage and track patient records efficiently
            </p>
          </div>

          {hasPatients && (
            <Button
              onClick={() => navigate("/demographics")}
              variant="primary"
              size="md"
              className="d-flex align-items-center gap-2"
            >
              <span style={{ fontSize: "1.2rem" }}>➕</span>
              <span>Add Patient</span>
            </Button>
          )}
        </div>

        <Row className="g-4 mb-4">
          <Col md={6} lg={4}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="p-4">
                <div className="d-flex align-items-center mb-2">
                  <div className="bg-primary bg-opacity-10 p-3 rounded-3 me-3">
                    <span style={{ fontSize: "1.5rem" }}>📋</span>
                  </div>
                  <div>
                    <h3 className="mb-0 fw-bold">{patients.length}</h3>
                    <p className="text-muted mb-0 small">Total Patients</p>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6} lg={4}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="p-4">
                <div className="d-flex align-items-center mb-2">
                  <div className="bg-success bg-opacity-10 p-3 rounded-3 me-3">
                    <span style={{ fontSize: "1.5rem" }}>✅</span>
                  </div>
                  <div>
                    <h3 className="mb-0 fw-bold">{patients.length}</h3>
                    <p className="text-muted mb-0 small">Active Records</p>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6} lg={4}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="p-4">
                <div className="d-flex align-items-center mb-2">
                  <div className="bg-info bg-opacity-10 p-3 rounded-3 me-3">
                    <span style={{ fontSize: "1.5rem" }}>📊</span>
                  </div>
                  <div>
                    <h3 className="mb-0 fw-bold">0</h3>
                    <p className="text-muted mb-0 small">This Month</p>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {!hasPatients ? (
          <Card className="border-0 shadow-sm">
            <Card.Body className="p-5 text-center">
              <h5 className="mb-3 fw-semibold">{t("dashboard.noRecords")}</h5>
              <p className="text-muted mb-4">
                Get started by adding your first patient record
              </p>
              <Button
                onClick={() => navigate("/language")}
                variant="primary"
                size="md"
                className="px-4"
              >
                <span className="me-2">➕</span>
                Add New Patient
              </Button>
            </Card.Body>
          </Card>
        ) : (
          <Card className="border-0 shadow-sm">
            <Card.Body className="p-4">
              <h5 className="mb-4 fw-semibold">Recent Patients</h5>
              <Table hover responsive className="align-middle">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Patient Name</th>
                    <th>Age</th>
                    <th>Gender</th>
                    <th>Status</th>
                    <th>Last Visit</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((patient, index) => (
                    <tr key={patient.id}>
                      <td>{index + 1}</td>
                      <td>{patient.name}</td>
                      <td>{patient.age}</td>
                      <td>{patient.gender}</td>
                      <td>
                        <Badge
                          bg={
                            patient.status === "Active"
                              ? "success"
                              : patient.status === "Completed"
                              ? "secondary"
                              : "warning"
                          }
                        >
                          {patient.status}
                        </Badge>
                      </td>
                      <td>{patient.lastVisit}</td>
                      <td>
                        <Button
                          size="sm"
                          variant="outline-primary"
                          onClick={() => alert(`Viewing ${patient.name}`)}
                        >
                          View
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              <ReactPaginate
                breakLabel="..."
                nextLabel="›"
                previousLabel="‹"
                onPageChange={handlePageClick}
                pageRangeDisplayed={3}
                pageCount={pageCount}
                renderOnZeroPageCount={null}
                containerClassName="pagination justify-content-center mt-3"
                pageClassName="page-item"
                pageLinkClassName="page-link"
                previousClassName="page-item"
                previousLinkClassName="page-link"
                nextClassName="page-item"
                nextLinkClassName="page-link"
                activeClassName="active"
              />
            </Card.Body>
          </Card>
        )}
      </Container>
    </div>
  );
}
