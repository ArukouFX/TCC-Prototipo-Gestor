import React, { useEffect } from 'react';
import '../styles/Notification.css';

const Notification = ({ message, type = 'info', duration = 3000, onClose }) => {
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [message, duration, onClose]);

  if (!message) return null;

  return (
    <div className={`notification ${type}`} role="alert">
      <div className="notification-content">
        {type === 'error' && <i className="fas fa-exclamation-circle" />}
        {type === 'success' && <i className="fas fa-check-circle" />}
        {type === 'info' && <i className="fas fa-info-circle" />}
        <span>{message}</span>
      </div>
      <button 
        className="notification-close" 
        onClick={() => onClose?.()} 
        aria-label="Cerrar notificación"
      >
        ×
      </button>
    </div>
  );
};

export default Notification;