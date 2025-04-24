import React from 'react';
import ScheduleCard from './ScheduleCard';

const TIME_SLOTS = [
  { start: '08:00:00', end: '10:00:00', display: '08:00 - 10:00' },
  { start: '10:00:00', end: '12:00:00', display: '10:00 - 12:00' },
  { start: '14:00:00', end: '16:00:00', display: '14:00 - 16:00' },
  { start: '16:00:00', end: '18:00:00', display: '16:00 - 18:00' },
  { start: '19:00:00', end: '21:00:00', display: '19:00 - 21:00' },
  { start: '21:00:00', end: '23:00:00', display: '21:00 - 23:00' }
];

const DAYS = [
  { id: 'MON', name: 'Lunes' },
  { id: 'TUE', name: 'Martes' },
  { id: 'WED', name: 'Miércoles' },
  { id: 'THU', name: 'Jueves' },
  { id: 'FRI', name: 'Viernes' }
];

const ScheduleTable = ({ schedules, filters }) => {
  // Filtra los horarios según los filtros activos
  const filteredSchedules = schedules.filter(schedule => {
    const matchesCourse = !filters.course || 
      (schedule.course && schedule.course.id === parseInt(filters.course));
    const matchesRoom = !filters.room || 
      (schedule.room && schedule.room.id === parseInt(filters.room));
    return matchesCourse && matchesRoom;
  });

  return (
    <div className="schedule-view">
      {/* Encabezado de la tabla */}
      <div className="schedule-header">
        <div className="time-column">Hora</div>
        {DAYS.map(day => (
          <div key={day.id} className="day-column">{day.name}</div>
        ))}
      </div>

      {/* Cuerpo de la tabla */}
      <div className="schedule-body">
        {TIME_SLOTS.map(slot => (
          <React.Fragment key={slot.start}>
            {/* Columna de hora */}
            <div className="time-slot">{slot.display}</div>

            {/* Celdas de días */}
            {DAYS.map(day => {
              const schedule = filteredSchedules.find(s => 
                s.day === day.id && 
                s.start_time === slot.start &&
                s.end_time === slot.end
              );

              return (
                <div key={`${day.id}-${slot.start}`} className="schedule-cell">
                  {schedule ? <ScheduleCard schedule={schedule} /> : null}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default ScheduleTable;