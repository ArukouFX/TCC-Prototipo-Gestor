import React, { useState, useEffect } from 'react';

const ScheduleEditor = ({ schedule, onSave, onCancel }) => {
  const [rooms, setRooms] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [editedSchedule, setEditedSchedule] = useState(schedule);

  useEffect(() => {
    setEditedSchedule(schedule);
  }, [schedule]);

  useEffect(() => {
    // Fetch rooms, teachers, and subjects when component mounts
    const fetchData = async () => {
      try {
        const [roomsResponse, teachersResponse, subjectsResponse] = await Promise.all([
          fetch('/api/rooms/'),
          fetch('/api/teachers/'),
          fetch('/api/subjects/')
        ]);

        const roomsData = await roomsResponse.json();
        const teachersData = await teachersResponse.json();
        const subjectsData = await subjectsResponse.json();

        setRooms(roomsData);
        setTeachers(teachersData);
        setSubjects(subjectsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const handleSave = () => {
    onSave(editedSchedule);
  };

  return (
    <div 
      className="schedule-editor"
      style={{
        position: 'fixed',
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 2000
      }}
    >
      <div className="editor-content">
        <h3>Edit Schedule</h3>
        <select 
          value={editedSchedule.subject?.id || ''}
          onChange={e => setEditedSchedule({
            ...editedSchedule,
            subject: subjects.find(s => s.id === parseInt(e.target.value))
          })}
        >
          <option value="" disabled>Select Subject</option>
          {subjects.map(subject => (
            <option key={subject.id} value={subject.id}>
              {subject.name}
            </option>
          ))}
        </select>
        <select 
          value={editedSchedule.room?.id || ''}
          onChange={e => setEditedSchedule({
            ...editedSchedule,
            room: rooms.find(r => r.id === parseInt(e.target.value))
          })}
        >
          <option value="" disabled>Select Room</option>
          {rooms.map(room => (
            <option key={room.id} value={room.id}>
              {room.name}
            </option>
          ))}
        </select>
        <select 
          value={editedSchedule.teacher?.id || ''}
          onChange={e => setEditedSchedule({
            ...editedSchedule,
            teacher: teachers.find(t => t.id === parseInt(e.target.value))
          })}
        >
          <option value="" disabled>Select Teacher</option>
          {teachers.map(teacher => (
            <option key={teacher.id} value={teacher.id}>
              {teacher.name}
            </option>
          ))}
        </select>
        <div className="editor-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default ScheduleEditor;