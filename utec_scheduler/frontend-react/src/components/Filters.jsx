import React from 'react';

const Filters = ({ filters, setFilters, courses, rooms }) => {
  return (
    <div className="controls-bar">
      <div className="filters">
        <select
          id="course-filter"
          className="filter-select"
          value={filters.course || ""}
          onChange={(e) => setFilters({ ...filters, course: e.target.value })}
        >
          <option value="">Todos los cursos</option>
          {courses.map(course => (
            <option key={course.id} value={course.id}>
              {course.name}
            </option>
          ))}
        </select>

        <select
          id="room-filter"
          className="filter-select"
          value={filters.room || ""}
          onChange={(e) => setFilters({ ...filters, room: e.target.value })}
        >
          <option value="">Todos los salones</option>
          {rooms.map(room => (
            <option key={room.id} value={room.id}>
              {room.name}
            </option>
          ))}
        </select>

        <button id="week-selector" className="time-selector active">
          Semana actual
        </button>
        <button id="day-selector" className="time-selector">
          Día
        </button>
      </div>

      <div className="actions">
        <button className="action-btn">
          <i className="fas fa-sync-alt"></i> Actualizar
        </button>
        <button className="action-btn primary">
          <i className="fas fa-plus"></i> Nuevo horario
        </button>
      </div>
    </div>
  );
};

export default Filters;