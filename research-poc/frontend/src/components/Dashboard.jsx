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
  const { useEffect } = React;
  const [patients, setPatients] = useState([]);
  const [stats, setStats] = useState({ total_patients: 0, active_records: 0, this_month: 0, recent_patients: [] });
  // fetch patients and dashboard stats from backend
  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const mod = await import('../api');
        const [patientsRes, statsRes] = await Promise.all([
          fetch(mod.api('/api/v1/patients')),
          fetch(mod.api('/api/v1/dashboard/stats')),
        ]);
        if (!mounted) return;
        const patientsJson = patientsRes.ok ? await patientsRes.json() : [];
        const statsJson = statsRes.ok ? await statsRes.json() : { total_patients: 0, active_records: 0, this_month: 0 };
        if (mounted) {
          setPatients(patientsJson || []);
          setStats(statsJson || { total_patients: 0, active_records: 0, this_month: 0, recent_patients: [] });
        }
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      }
    };

    // initial load
    load();

    // refetch when window/tab regains focus or visibility
    const onFocus = () => {
      if (document.visibilityState === 'visible') {
        load();
      }
    };
    window.addEventListener('focus', onFocus);
    document.addEventListener('visibilitychange', onFocus);

    return () => {
      mounted = false;
      window.removeEventListener('focus', onFocus);
      document.removeEventListener('visibilitychange', onFocus);
    };
  }, []);
  const itemsPerPage = 3;
  const [itemOffset, setItemOffset] = useState(0);

  const endOffset = itemOffset + itemsPerPage;
  const currentItems = patients.slice(itemOffset, endOffset);
  const pageCount = Math.ceil(patients.length / itemsPerPage);

  const handlePageClick = (event) => {
    const newOffset = (event.selected * itemsPerPage) % patients.length;
    setItemOffset(newOffset);
  };
  const hasPatients = patients && patients.length > 0;

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

          {(
            <Button
              onClick={() => {
                // start a new patient flow; frontend will create patient on StepOne submit
                navigate('/demographics');
              }}
              variant="primary"
              size="md"
              className="d-flex align-items-center gap-2"
            >
              <span style={{ fontSize: '1.2rem' }}>➕</span>
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
                    <h3 className="mb-0 fw-bold">{stats.total_patients ?? patients.length}</h3>
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
                    <h3 className="mb-0 fw-bold">{stats.active_records ?? patients.length}</h3>
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
                    <h3 className="mb-0 fw-bold">{stats.this_month ?? 0}</h3>
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
                onClick={() => navigate("/demographics")}
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
                      <td className="d-flex gap-2">
                        <Button
                          size="sm"
                          variant="outline-primary"
                          onClick={() => navigate(`/patients/${patient.id}`)}
                        >
                          View
                        </Button>
                        <Button
                          size="sm"
                          variant="outline-danger"
                          onClick={async () => {
                            if (!window.confirm(`Delete patient ${patient.name || patient.id}? This action cannot be undone.`)) return;
                            try {
                              const mod = await import('../api');
                              const res = await fetch(mod.api(`/api/v1/patients/${patient.id}`), { method: 'DELETE' });
                              if (res.ok || res.status === 204) {
                                // remove from local list and refresh stats
                                setPatients((prev) => prev.filter((p) => p.id !== patient.id));
                                try {
                                  const mod2 = await import('../api');
                                  const r = await fetch(mod2.api('/api/v1/dashboard/stats'));
                                  if (r.ok) {
                                    const s = await r.json();
                                    setStats(s || { total_patients: 0, active_records: 0, this_month: 0, recent_patients: [] });
                                  }
                                } catch (e) {
                                  console.warn('Failed to refresh stats after delete', e);
                                }
                                return;
                              }
                              const txt = await res.text();
                              throw new Error(txt || `Failed to delete (${res.status})`);
                            } catch (err) {
                              console.error('Delete failed', err);
                              alert('Failed to delete patient: ' + (err.message || err));
                            }
                          }}
                        >
                          Delete
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
