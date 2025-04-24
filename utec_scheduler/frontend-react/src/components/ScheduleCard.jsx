import React from 'react';

const ScheduleCard = ({ schedule }) => {
  if (!schedule) return null;

  // Validar que los objetos necesarios existan
  const { subject, teacher, room, course } = schedule;

  if (!subject?.name || !teacher?.name || !room?.name || !course?.name) {
    console.error('Invalid schedule data:', schedule);
    return null;
  }

  return (
    <div className="schedule-card" data-id={schedule.id}>
      <div className="card-header">
        <span className="subject-name">{subject.name}</span>
        <span className="room-name">{room.name}</span>
      </div>
      
      <div className="card-body">
        <p className="course-name">{course.name}</p>
        <p className="teacher-name">{teacher.name}</p>
      </div>
      
      <div className="card-actions">
        <button 
          className="edit-btn" 
          data-id={schedule.id}
          aria-label="Editar horario"
        >
          <i className="fas fa-edit"></i>
        </button>
        <button 
          className="delete-btn" 
          data-id={schedule.id}
          aria-label="Eliminar horario"
        >
          <i className="fas fa-trash"></i>
        </button>
      </div>
    </div>
  );
};

export default ScheduleCard;