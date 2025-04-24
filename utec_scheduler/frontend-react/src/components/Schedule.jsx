import React, { useState } from 'react';
import TimeSlotEditor from './TimeSlotEditor';
import ScheduleEditor from './ScheduleEditor';

const Schedule = ({ schedules, onScheduleChange }) => {
  const [editingTimeSlot, setEditingTimeSlot] = useState(null);
  const [editingSchedule, setEditingSchedule] = useState(null);

  // Generar solo las horas base (ej: 19:00, 20:00, 21:00, 22:00)
  const hourRange = [19, 20, 21, 22];
  const baseHours = hourRange.map(h => `${h.toString().padStart(2, '0')}:00`);
  const days = ['MON', 'TUE', 'WED', 'THU', 'FRI'];

  // Ordenar horarios por día y hora
  const sortedSchedules = [...schedules].sort((a, b) => {
    const dayOrder = { MON: 0, TUE: 1, WED: 2, THU: 3, FRI: 4 };
    if (a.day !== b.day) return dayOrder[a.day] - dayOrder[b.day];
    return a.start_time.localeCompare(b.start_time);
  });

  // Utilidad para saber si una celda ya está cubierta por un bloque anterior
  const isCellCovered = (day, hour, schedules) => {
    return schedules.some(sch => {
      if (sch.day !== day) return false;
      const schStart = sch.start_time.slice(0,5);
      const schDuration = Math.ceil(sch.duration / 60);
      const schStartIdx = baseHours.indexOf(schStart);
      if (schStartIdx === -1) return false;
      const hourIdx = baseHours.indexOf(hour);
      return schStartIdx < hourIdx && schStartIdx + schDuration > hourIdx;
    });
  };

  // Renderizar la celda de horario, permitiendo múltiples bloques simultáneos
  const renderScheduleCell = (day, hour) => {
    // Buscar todos los horarios que coinciden con el slot y el día
    const schedulesInCell = sortedSchedules.filter(
      sch => sch.day === day && sch.start_time.slice(0,5) === hour
    );
    if (schedulesInCell.length > 0) {
      // Si hay más de uno, apilar las tarjetas en la celda
      return (
        <td
          className="schedule-cell"
          key={`${hour}-${day}`}
          rowSpan={1} // Cada bloque se apila, no se alarga
        >
          {schedulesInCell.map(schedule => (
            <div className="schedule-card" key={schedule.id} style={{ marginBottom: '4px' }}>
              <div className="card-header">
                <span className="subject-name">{schedule.subject.name}</span>
                <span className="room-name">{schedule.room.name}</span>
              </div>
              <div className="card-body">
                <p className="course-name">{schedule.course.name}</p>
                <p className="teacher-name">{schedule.teacher.name}</p>
                <p style={{ fontSize: '0.8em', color: '#888' }}>
                  {schedule.start_time.slice(0,5)} - {schedule.end_time.slice(0,5)}
                </p>
              </div>
              <div className="card-actions">
                <button
                  className="edit-btn"
                  onClick={(e) => handleEditClick(schedule, e)}
                  title="Edit"
                >
                  <i className="fas fa-edit"></i>
                </button>
                <button
                  className="delete-btn"
                  onClick={(e) => handleDeleteClick(schedule, e)}
                  title="Delete"
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>
          ))}
        </td>
      );
    }
    // Si la celda está cubierta por un bloque anterior, no renderizar nada
    if (isCellCovered(day, hour, sortedSchedules)) {
      return null;
    }
    return <td className="schedule-cell" key={`${hour}-${day}`}></td>;
  };

  const handleDeleteClick = async (schedule, event) => {
    event.stopPropagation();
    if (window.confirm('Are you sure you want to delete this schedule?')) {
      try {
        const response = await fetch(`/api/schedules/${schedule.id}/`, {
          method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete schedule');
        const updatedSchedules = schedules.filter(s => s.id !== schedule.id);
        onScheduleChange(updatedSchedules);
      } catch (error) {
        console.error('Error deleting schedule:', error);
        alert('Failed to delete schedule');
      }
    }
  };

  const handleEditClick = (schedule, event) => {
    event.stopPropagation();
    setEditingSchedule({ schedule });
  };

  const handleScheduleSave = async (updatedSchedule) => {
    try {
      const response = await fetch(`/api/schedules/${updatedSchedule.id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedSchedule)
      });
      if (!response.ok) throw new Error('Failed to update schedule');
      const updatedSchedules = schedules.map(schedule => 
        schedule.id === updatedSchedule.id ? updatedSchedule : schedule
      );
      onScheduleChange(updatedSchedules);
      setEditingSchedule(null);
    } catch (error) {
      console.error('Error updating schedule:', error);
      alert('Failed to update schedule');
    }
  };

  return (
    <div className="schedule-view">
      <table className="schedule-table">
        <thead>
          <tr>
            <th>Hora</th>
            <th>Lunes</th>
            <th>Martes</th>
            <th>Miércoles</th>
            <th>Jueves</th>
            <th>Viernes</th>
          </tr>
        </thead>
        <tbody>
          {baseHours.map((hour, rowIdx) => (
            <tr key={hour}>
              <td className="time-slot">{hour}</td>
              {days.map(day => renderScheduleCell(day, hour))}
            </tr>
          ))}
        </tbody>
      </table>
      {editingTimeSlot && (
        <TimeSlotEditor
          timeSlot={editingTimeSlot.time}
          position={editingTimeSlot.position}
          onSave={(newTime) => handleTimeSlotSave(editingTimeSlot.time, newTime)}
          onCancel={() => setEditingTimeSlot(null)}
        />
      )}
      {editingSchedule && (
        <ScheduleEditor
          schedule={editingSchedule.schedule}
          onSave={handleScheduleSave}
          onCancel={() => setEditingSchedule(null)}
        />
      )}
    </div>
  );
};

export default Schedule;