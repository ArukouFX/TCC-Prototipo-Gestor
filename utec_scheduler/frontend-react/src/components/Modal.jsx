import React, { useState, useEffect } from 'react';

const Modal = ({ open, onClose, onSave, schedule = null }) => {
  const [formData, setFormData] = useState({
    course: '',
    subject: '',
    teacher: '',
    room: '',
    day: 'MON',
    start_time: '',
    end_time: ''
  });

  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);

  useEffect(() => {
    if (schedule) {
      setFormData({
        course: schedule.course?.id || '',
        subject: schedule.subject?.id || '',
        teacher: schedule.teacher?.id || '',
        room: schedule.room?.id || '',
        day: schedule.day || 'MON',
        start_time: schedule.start_time?.slice(0, 5) || '',
        end_time: schedule.end_time?.slice(0, 5) || ''
      });
    }
  }, [schedule]);

  // Cargar materias cuando cambia el curso
  useEffect(() => {
    if (formData.course) {
      fetch(`/api/subjects/?course=${formData.course}`)
        .then(res => res.json())
        .then(setSubjects);
    }
  }, [formData.course]);

  // Cargar profesores cuando cambia la materia
  useEffect(() => {
    if (formData.subject) {
      fetch(`/api/teachers/?subject=${formData.subject}`)
        .then(res => res.json())
        .then(setTeachers);
    }
  }, [formData.subject]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!open) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{schedule ? 'Editar Horario' : 'Nuevo Horario'}</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="course">Curso:</label>
            <select
              id="course"
              value={formData.course}
              onChange={e => setFormData({ ...formData, course: e.target.value })}
              required
            >
              <option value="">Seleccione un curso</option>
              {courses.map(course => (
                <option key={course.id} value={course.id}>{course.name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="subject">Materia:</label>
            <select
              id="subject"
              value={formData.subject}
              onChange={e => setFormData({ ...formData, subject: e.target.value })}
              required
            >
              <option value="">Seleccione una materia</option>
              {subjects.map(subject => (
                <option key={subject.id} value={subject.id}>
                  {subject.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="teacher">Profesor:</label>
            <select
              id="teacher"
              value={formData.teacher}
              onChange={e => setFormData({ ...formData, teacher: e.target.value })}
              required
            >
              <option value="">Seleccione un profesor</option>
              {teachers.map(teacher => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="room">Salón:</label>
            <select
              id="room"
              value={formData.room}
              onChange={e => setFormData({ ...formData, room: e.target.value })}
              required
            >
              <option value="">Seleccione un salón</option>
              {rooms.map(room => (
                <option key={room.id} value={room.id}>{room.name}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="day">Día:</label>
              <select
                id="day"
                value={formData.day}
                onChange={e => setFormData({ ...formData, day: e.target.value })}
                required
              >
                <option value="MON">Lunes</option>
                <option value="TUE">Martes</option>
                <option value="WED">Miércoles</option>
                <option value="THU">Jueves</option>
                <option value="FRI">Viernes</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="start_time">Hora inicio:</label>
              <input
                type="time"
                id="start_time"
                value={formData.start_time}
                onChange={e => setFormData({ ...formData, start_time: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="end_time">Hora fin:</label>
              <input
                type="time"
                id="end_time"
                value={formData.end_time}
                onChange={e => setFormData({ ...formData, end_time: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn secondary">
              Cancelar
            </button>
            <button type="submit" className="btn primary">
              {schedule ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Modal;