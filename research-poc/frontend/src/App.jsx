import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import LanguageSelection from "./components/LanguageSelection";
import "./i18";
import StepOne from "./components/StepOne";
import StepTwo from "./components/StepTwo";
import StepThree from "./components/StepThree";
import AppNavbar from "./components/Navbar";
import PatientView from "./components/PatientView";

export default function App() {
  return (
    <Router>
      <AppNavbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/language" element={<LanguageSelection />} />
        <Route path="/demographics" element={<StepOne />} />
        <Route path="/lifestyle" element={<StepTwo />} />
        <Route path="/wearable" element={<StepThree />} />
  <Route path="/patients/:id" element={<PatientView />} />
      </Routes>
    </Router>
  );
}
