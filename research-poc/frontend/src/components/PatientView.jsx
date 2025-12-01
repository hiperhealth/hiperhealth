import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Card, Button } from 'react-bootstrap';

export default function PatientView(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);

  useEffect(()=>{
    import('../api').then(({ api })=>{
      fetch(api(`/api/v1/patients/${id}`))
        .then(r=>{
          if(!r.ok) throw new Error('Not found');
          return r.json();
        })
        .then(j=>setPatient(j))
        .catch(e=>console.error(e));
    })
  },[id]);

  if(!patient) return (
    <Container className="mt-5">Loading...</Container>
  );

  return (
    <Container className="mt-5">
      <Button variant="link" onClick={()=>navigate(-1)}>← Back</Button>
      <Card className="mt-3">
        <Card.Body>
          <h3>{patient.name || 'Patient'}</h3>
          <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(patient, null, 2)}</pre>
        </Card.Body>
      </Card>
    </Container>
  )
}
