import React, { useState, useEffect, useRef } from 'react';

const TimeSlotEditor = ({ schedule, onSave, onCancel, position }) => {
  const [startTime, setStartTime] = useState(schedule ? schedule.start_time.slice(0,5) : '');
  const [duration, setDuration] = useState(schedule ? schedule.duration : 120);
  const [endTime, setEndTime] = useState(schedule ? schedule.end_time.slice(0,5) : '');
  const editorRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (editorRef.current && !editorRef.current.contains(event.target)) {
        onCancel();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onCancel]);

  const handleDurationChange = (e) => {
    const value = parseInt(e.target.value, 10);
    setDuration(value);
    // Ajustar end_time automáticamente
    const [h, m] = startTime.split(":").map(Number);
    const end = new Date(0, 0, 0, h, m + value);
    setEndTime(end.toTimeString().slice(0,5));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Validate time format (HH:mm)
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
    if (!timeRegex.test(startTime)) {
      alert('Please enter a valid time in HH:mm format');
      return;
    }
    onSave({
      start_time: startTime,
      duration: duration,
      end_time: endTime + ':00',
    });
  };

  return (
    <div 
      ref={editorRef}
      className="time-slot-edit"
      style={{
        left: position.x,
        top: position.y
      }}
    >
      <form onSubmit={handleSubmit}>
        <label>Hora de inicio:
          <input
            type="time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            step="1800"
          />
        </label>
        <label>Duración:
          <select value={duration} onChange={handleDurationChange}>
            <option value={120}>2 horas</option>
            <option value={180}>3 horas</option>
          </select>
        </label>
        <div>
          <button className="save" type="submit">Guardar</button>
          <button className="cancel" onClick={onCancel}>Cancelar</button>
        </div>
      </form>
    </div>
  );
};

export default TimeSlotEditor;