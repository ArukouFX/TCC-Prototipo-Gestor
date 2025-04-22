/**
 * UTEC Scheduler - Gestor de Horarios Académicos
 * Aplicación Vanilla JS para gestión de horarios
 * Conexión con API REST en puerto 8000
 */

// Constantes de configuración
const API_BASE_URL = '/api'; // Proxy configurado en Nginx
const DAYS = {
    MON: 'Lunes',
    TUE: 'Martes',
    WED: 'Miércoles',
    THU: 'Jueves',
    FRI: 'Viernes'
};
const TIME_SLOTS = [
    '08:00 - 10:00',
    '10:00 - 12:00',
    '14:00 - 16:00',
    '16:00 - 18:00',
    '19:00 - 21:00'
];

// Estado global de la aplicación
let state = {
    schedules: [],
    courses: [],
    subjects: [],
    teachers: [],
    rooms: [],
    currentFilters: {
        course: null,
        room: null
    }
};

// Elementos del DOM
const domElements = {
    scheduleBody: document.getElementById('schedule-body'),
    courseFilter: document.getElementById('course-filter'),
    roomFilter: document.getElementById('room-filter'),
    refreshBtn: document.getElementById('refresh-btn'),
    newScheduleBtn: document.getElementById('new-schedule-btn'),
    modal: document.getElementById('schedule-modal'),
    modalTitle: document.getElementById('modal-title'),
    scheduleForm: document.getElementById('schedule-form'),
    scheduleIdInput: document.getElementById('schedule-id'),
    modalCourseSelect: document.getElementById('modal-course'),
    modalSubjectSelect: document.getElementById('modal-subject'),
    modalTeacherSelect: document.getElementById('modal-teacher'),
    modalRoomSelect: document.getElementById('modal-room'),
    modalDaySelect: document.getElementById('modal-day'),
    modalStartTime: document.getElementById('modal-start-time'),
    modalEndTime: document.getElementById('modal-end-time'),
    cancelBtn: document.getElementById('cancel-btn'),
    notification: document.getElementById('notification')
};

// Inicialización de la aplicación
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadInitialData();
});

/**
 * Inicializa los event listeners
 */
function initEventListeners() {
    // Filtros
    domElements.courseFilter.addEventListener('change', (e) => {
        state.currentFilters.course = e.target.value || null;
        renderSchedule();
    });
    
    domElements.roomFilter.addEventListener('change', (e) => {
        state.currentFilters.room = e.target.value || null;
        renderSchedule();
    });
    
    // Botones
    domElements.refreshBtn.addEventListener('click', loadInitialData);
    domElements.newScheduleBtn.addEventListener('click', openScheduleModal);
    domElements.cancelBtn.addEventListener('click', closeModal);
    
    // Modal y formulario
    domElements.scheduleForm.addEventListener('submit', handleFormSubmit);
    domElements.modal.addEventListener('click', (e) => {
        if (e.target === domElements.modal) closeModal();
    });
    
    // Delegación de eventos para los horarios
    domElements.scheduleBody.addEventListener('click', (e) => {
        const scheduleCard = e.target.closest('.schedule-card');
        if (!scheduleCard) return;
        
        const editBtn = e.target.closest('.edit-btn');
        const deleteBtn = e.target.closest('.delete-btn');
        
        if (editBtn) {
            const scheduleId = parseInt(editBtn.dataset.id);
            openScheduleModal(scheduleId);
        }
        
        if (deleteBtn) {
            const scheduleId = parseInt(deleteBtn.dataset.id);
            deleteSchedule(scheduleId);
        }
    });
}

/**
 * Carga los datos iniciales de la aplicación
 */
async function loadInitialData() {
    try {
        showLoading(true);
        
        const [schedules, courses, subjects, teachers, rooms] = await Promise.all([
            fetchData('schedules'),
            fetchData('courses'),
            fetchData('subjects'),
            fetchData('teachers'),
            fetchData('rooms')
        ]);
        
        state = {
            ...state,
            schedules,
            courses,
            subjects,
            teachers,
            rooms
        };
        
        populateFilters();
        populateModalSelects();
        renderSchedule();
        showNotification('Datos actualizados correctamente', 'success');
    } catch (error) {
        console.error('Error loading initial data:', error);
        showNotification('Error al cargar los datos', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Realiza una petición a la API
 */
async function fetchData(endpoint) {
    const response = await fetch(`${API_BASE_URL}/${endpoint}/`);
    if (!response.ok) {
        throw new Error(`Error fetching ${endpoint}`);
    }
    return await response.json();
}

/**
 * Renderiza el horario en la interfaz
 */
function renderSchedule() {
    const filteredSchedules = filterSchedules();
    const scheduleHTML = generateScheduleHTML(filteredSchedules);
    domElements.scheduleBody.innerHTML = scheduleHTML;
}

/**
 * Filtra los horarios según los filtros activos
 */
function filterSchedules() {
    return state.schedules.filter(schedule => {
        const matchesCourse = !state.currentFilters.course || 
                             schedule.course === parseInt(state.currentFilters.course);
        const matchesRoom = !state.currentFilters.room || 
                           schedule.room === parseInt(state.currentFilters.room);
        return matchesCourse && matchesRoom;
    });
}

/**
 * Genera el HTML para la tabla de horarios
 */
function generateScheduleHTML(schedules) {
    let html = '';
    TIME_SLOTS.forEach(timeSlot => {
        const [startTime, endTime] = timeSlot.split(' - ');
        // Columna de hora
        html += `<div class="time-slot">${timeSlot}</div>`;
        // Celdas de días (siempre 5)
        ['MON', 'TUE', 'WED', 'THU', 'FRI'].forEach(day => {
            const schedule = schedules.find(s =>
                s.day === day &&
                s.start_time.startsWith(startTime) &&
                s.end_time.startsWith(endTime)
            );
            html += schedule
                ? `<div class="schedule-cell">${generateScheduleCard(schedule)}</div>`
                : `<div class="schedule-cell empty-slot" data-day="${day}" data-time="${timeSlot}"></div>`;
        });
    });
    return html;
}

/**
 * Genera el HTML para una tarjeta de horario
 */
function generateScheduleCard(schedule) {
    const course = state.courses.find(c => c.id === schedule.course);
    const subject = state.subjects.find(s => s.id === schedule.subject);
    const teacher = state.teachers.find(t => t.id === schedule.teacher);
    const room = state.rooms.find(r => r.id === schedule.room);
    
    return `
        <div class="schedule-card" data-id="${schedule.id}">
            <div class="card-header">
                <span class="subject-name">${subject.name}</span>
                <span class="room-name">${room.name}</span>
            </div>
            <div class="card-body">
                <p class="course-name">${course.name}</p>
                <p class="teacher-name">${teacher.name}</p>
            </div>
            <div class="card-actions">
                <button class="edit-btn" data-id="${schedule.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="delete-btn" data-id="${schedule.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

/**
 * Rellena los selectores de filtro
 */
function populateFilters() {
    // Cursos
    domElements.courseFilter.innerHTML = `
        <option value="">Todos los cursos</option>
        ${state.courses.map(course => `
            <option value="${course.id}">${course.name}</option>
        `).join('')}
    `;
    
    // Salones
    domElements.roomFilter.innerHTML = `
        <option value="">Todos los salones</option>
        ${state.rooms.map(room => `
            <option value="${room.id}">${room.name}</option>
        `).join('')}
    `;
}

/**
 * Rellena los selectores del modal
 */
function populateModalSelects() {
    // Cursos
    domElements.modalCourseSelect.innerHTML = `
        <option value="">Seleccione un curso</option>
        ${state.courses.map(course => `
            <option value="${course.id}">${course.name}</option>
        `).join('')}
    `;
    
    // Materias
    domElements.modalSubjectSelect.innerHTML = `
        <option value="">Seleccione una materia</option>
        ${state.subjects.map(subject => `
            <option value="${subject.id}">${subject.name} (${subject.code})</option>
        `).join('')}
    `;
    
    // Profesores
    domElements.modalTeacherSelect.innerHTML = `
        <option value="">Seleccione un profesor</option>
        ${state.teachers.map(teacher => `
            <option value="${teacher.id}">${teacher.name}</option>
        `).join('')}
    `;
    
    // Salones
    domElements.modalRoomSelect.innerHTML = `
        <option value="">Seleccione un salón</option>
        ${state.rooms.map(room => `
            <option value="${room.id}">${room.name} (${getRoomTypeName(room.room_type)})</option>
        `).join('')}
    `;
}

/**
 * Abre el modal para crear/editar un horario
 */
function openScheduleModal(scheduleId = null) {
    if (scheduleId) {
        // Modo edición
        const schedule = state.schedules.find(s => s.id === scheduleId);
        if (!schedule) return;
        
        domElements.modalTitle.textContent = 'Editar Horario';
        domElements.scheduleIdInput.value = schedule.id;
        domElements.modalCourseSelect.value = schedule.course;
        domElements.modalSubjectSelect.value = schedule.subject;
        domElements.modalTeacherSelect.value = schedule.teacher;
        domElements.modalRoomSelect.value = schedule.room;
        domElements.modalDaySelect.value = schedule.day;
        domElements.modalStartTime.value = schedule.start_time.substring(0, 5);
        domElements.modalEndTime.value = schedule.end_time.substring(0, 5);
    } else {
        // Modo creación
        domElements.modalTitle.textContent = 'Nuevo Horario';
        domElements.scheduleForm.reset();
        domElements.scheduleIdInput.value = '';
    }
    
    domElements.modal.style.display = 'block';
}

/**
 * Cierra el modal
 */
function closeModal() {
    domElements.modal.style.display = 'none';
}

/**
 * Maneja el envío del formulario
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        course: domElements.modalCourseSelect.value,
        subject: domElements.modalSubjectSelect.value,
        teacher: domElements.modalTeacherSelect.value,
        room: domElements.modalRoomSelect.value,
        day: domElements.modalDaySelect.value,
        start_time: domElements.modalStartTime.value + ':00',
        end_time: domElements.modalEndTime.value + ':00'
    };
    
    const scheduleId = domElements.scheduleIdInput.value;
    const isEdit = !!scheduleId;
    
    try {
        showLoading(true);
        
        const url = isEdit 
            ? `${API_BASE_URL}/schedules/${scheduleId}/` 
            : `${API_BASE_URL}/schedules/`;
            
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Error al guardar');
        }
        
        closeModal();
        await loadInitialData();
        showNotification(
            isEdit ? 'Horario actualizado' : 'Horario creado', 
            'success'
        );
    } catch (error) {
        console.error('Error saving schedule:', error);
        showNotification(error.message || 'Error al guardar', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Elimina un horario
 */
async function deleteSchedule(scheduleId) {
    if (!confirm('¿Está seguro que desea eliminar este horario?')) return;
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/schedules/${scheduleId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });
        
        if (!response.ok) {
            throw new Error('Error al eliminar');
        }
        
        await loadInitialData();
        showNotification('Horario eliminado', 'success');
    } catch (error) {
        console.error('Error deleting schedule:', error);
        showNotification('Error al eliminar el horario', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Muestra una notificación
 */
function showNotification(message, type = 'info') {
    domElements.notification.textContent = message;
    domElements.notification.className = `notification ${type}`;
    domElements.notification.classList.remove('hidden');
    
    setTimeout(() => {
        domElements.notification.classList.add('hidden');
    }, 3000);
}

/**
 * Muestra/oculta el estado de carga
 */
function showLoading(show) {
    if (show) {
        document.body.classList.add('loading');
    } else {
        document.body.classList.remove('loading');
    }
}

/**
 * Obtiene el nombre del tipo de sala
 */
function getRoomTypeName(roomType) {
    const types = {
        'CLASS': 'Aula',
        'MULTI': 'Multipropósito',
        'COWORK': 'Coworking',
        'COMP': 'Lab. Informática',
        'LOG': 'Lab. Logística'
    };
    return types[roomType] || roomType;
}

/**
 * Obtiene el valor de una cookie
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}