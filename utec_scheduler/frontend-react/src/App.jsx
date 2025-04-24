import { useState, useEffect } from "react";
import Schedule from "./components/Schedule";
import Filters from "./components/Filters";
import Modal from "./components/Modal";
import Notification from "./components/Notification";
import "./App.css";

function App() {
  const [schedules, setSchedules] = useState([]);
  const [courses, setCourses] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [filters, setFilters] = useState({ course: "", room: "" });
  const [modalOpen, setModalOpen] = useState(false);
  const [notification, setNotification] = useState({ message: "", type: "" });

  // Cargar datos iniciales
  useEffect(() => {
    fetch("/api/schedules/")
      .then(res => res.json())
      .then(data => {
        // Si viene como {schedules: [...]}, usar schedules; si es array, usar data
        if (Array.isArray(data)) {
          setSchedules(data);
        } else if (Array.isArray(data.schedules)) {
          setSchedules(data.schedules);
        } else {
          setSchedules([]);
        }
      });
    fetch("/api/courses/")
      .then(res => res.json())
      .then(setCourses);
    fetch("/api/rooms/")
      .then(res => res.json())
      .then(setRooms);
  }, []);

  // Manejar cambios en los horarios (edición/eliminación)
  const handleScheduleChange = (updatedSchedules) => {
    setSchedules(updatedSchedules);
  };

  return (
    <div>
      <h1>Gestor de Horarios Académicos</h1>
      <Filters
        filters={filters}
        setFilters={setFilters}
        courses={courses}
        rooms={rooms}
      />
      <button onClick={() => setModalOpen(true)}>Nuevo horario</button>
      <Schedule
        schedules={schedules}
        onScheduleChange={handleScheduleChange}
      />
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} />
      <Notification 
        message={notification.message}
        type={notification.type}
        onClose={() => setNotification({ message: '', type: '' })}
      />
    </div>
  );
}

export default App;