document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const scheduleTable = document.getElementById('schedule-table');
    const refreshBtn = document.getElementById('refresh-btn');
    const newScheduleBtn = document.getElementById('new-schedule-btn');
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close');
    const scheduleForm = document.getElementById('schedule-form');
    
    // Variables globales
    let schedules = [];
    let courses = [];
    let subjects = [];
    let teachers = [];
    let rooms = [];
    
    // Inicializar la aplicación
    init();
    
    // Función de inicialización
    function init() {
        loadAllData();
        setupEventListeners();
    }
    
    // Cargar todos los datos necesarios
    async function loadAllData() {
        try {
            const responses = await Promise.all([
                fetch('/api/schedules/').then(res => res.json()),
                fetch('/api/courses/').then(res => res.json()),
                fetch('/api/subjects/').then(res => res.json()),
                fetch('/api/teachers/').then(res => res.json()),
                fetch('/api/rooms/').then(res => res.json())
            ]);
            
            [schedules, courses, subjects, teachers, rooms] = responses;
            renderScheduleTable();
            populateDropdowns();
        } catch (error) {
            console.error('Error cargando datos:', error);
            alert('Error al cargar los datos. Por favor recarga la página.');
        }
    }
    
    // Renderizar la tabla de horarios
    function renderScheduleTable() {
        const tbody = scheduleTable.querySelector('tbody');
        tbody.innerHTML = '';
        
        // Horas del día (personaliza según tus necesidades)
        const timeSlots = [
            '08:00 - 10:00',
            '10:00 - 12:00',
            '14:00 - 16:00',
            '16:00 - 18:00',
            '19:00 - 21:00'
        ];
        
        timeSlots.forEach(timeSlot => {
            const row = document.createElement('tr');
            const timeCell = document.createElement('td');
            timeCell.textContent = timeSlot;
            row.appendChild(timeCell);
            
            // Celdas para cada día
            ['MON', 'TUE', 'WED', 'THU', 'FRI'].forEach(day => {
                const cell = document.createElement('td');
                
                // Buscar horarios para esta hora y día
                const [startTime, endTime] = timeSlot.split(' - ');
                const schedule = schedules.find(s => 
                    s.day === day && 
                    s.start_time.startsWith(startTime) && 
                    s.end_time.startsWith(endTime)
                );
                
                if (schedule) {
                    const course = courses.find(c => c.id === schedule.course);
                    const subject = subjects.find(s => s.id === schedule.subject);
                    const teacher = teachers.find(t => t.id === schedule.teacher);
                    const room = rooms.find(r => r.id === schedule.room);
                    
                    cell.innerHTML = `
                        <div class="schedule-card">
                            <strong>${subject.name}</strong>
                            <p>${course.name}</p>
                            <p>Prof: ${teacher.name}</p>
                            <p>Sala: ${room.name}</p>
                            <div class="actions">
                                <button class="edit-btn" data-id="${schedule.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="delete-btn" data-id="${schedule.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    `;
                } else {
                    cell.innerHTML = '<button class="add-btn">+</button>';
                    cell.querySelector('.add-btn').addEventListener('click', () => openModal(null, day, timeSlot));
                }
                
                row.appendChild(cell);
            });
            
            tbody.appendChild(row);
        });
    }
    
    // Llenar dropdowns del formulario
    function populateDropdowns() {
        const courseSelect = document.getElementById('course');
        const subjectSelect = document.getElementById('subject');
        
        courseSelect.innerHTML = courses.map(c => 
            `<option value="${c.id}">${c.name} (${c.shift})</option>`
        ).join('');
        
        subjectSelect.innerHTML = subjects.map(s => 
            `<option value="${s.id}">${s.name} (${s.code})</option>`
        ).join('');
    }
    
    // Abrir modal para editar/crear
    function openModal(scheduleId = null, day = null, timeSlot = null) {
        const modalTitle = document.getElementById('modal-title');
        const form = document.getElementById('schedule-form');
        
        if (scheduleId) {
            modalTitle.textContent = 'Editar Horario';
            const schedule = schedules.find(s => s.id === scheduleId);
            // Rellenar formulario con datos existentes
            document.getElementById('schedule-id').value = schedule.id;
            document.getElementById('course').value = schedule.course;
            document.getElementById('subject').value = schedule.subject;
            // ... otros campos
        } else {
            modalTitle.textContent = 'Nuevo Horario';
            form.reset();
            // Establecer día y hora si es nuevo
            if (day && timeSlot) {
                const [startTime, endTime] = timeSlot.split(' - ');
                // Aquí podrías establecer campos ocultos para día y hora
            }
        }
        
        modal.style.display = 'block';
    }
    
    // Configurar event listeners
    function setupEventListeners() {
        // Botón de refrescar
        refreshBtn.addEventListener('click', loadAllData);
        
        // Botón de nuevo horario
        newScheduleBtn.addEventListener('click', () => openModal());
        
        // Cerrar modal
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        // Clic fuera del modal para cerrar
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        // Enviar formulario
        scheduleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                course: document.getElementById('course').value,
                subject: document.getElementById('subject').value,
                teacher: document.getElementById('teacher').value,
                room: document.getElementById('room').value,
                day: document.getElementById('day').value,
                start_time: document.getElementById('start_time').value,
                end_time: document.getElementById('end_time').value
            };
            
            const scheduleId = document.getElementById('schedule-id').value;
            const url = scheduleId ? `/api/schedules/${scheduleId}/` : '/api/schedules/';
            const method = scheduleId ? 'PUT' : 'POST';
            
            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    loadAllData();
                    modal.style.display = 'none';
                } else {
                    const error = await response.json();
                    throw new Error(error.message || 'Error al guardar');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al guardar: ' + error.message);
            }
        });
        
        // Delegación de eventos para botones de editar/eliminar
        scheduleTable.addEventListener('click', (e) => {
            if (e.target.closest('.edit-btn')) {
                const scheduleId = e.target.closest('.edit-btn').dataset.id;
                openModal(scheduleId);
            }
            
            if (e.target.closest('.delete-btn')) {
                const scheduleId = e.target.closest('.delete-btn').dataset.id;
                if (confirm('¿Estás seguro de eliminar este horario?')) {
                    deleteSchedule(scheduleId);
                }
            }
        });
    }
    
    // Eliminar horario
    async function deleteSchedule(scheduleId) {
        try {
            const response = await fetch(`/api/schedules/${scheduleId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });
            
            if (response.ok) {
                loadAllData();
            } else {
                throw new Error('Error al eliminar');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar horario');
        }
    }
    
    // Función auxiliar para obtener cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

document.getElementById('generate-btn').addEventListener('click', async () => {
    const response = await fetch('/generate-schedules/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    });
    
    const data = await response.json();
    if (data.status === 'success') {
        alert('Horario generado con éxito!');
        location.reload();  // Refrescar para ver los cambios
    }
});