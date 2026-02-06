document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    
    if (alerts.length > 0) {
        setTimeout(function () {
            alerts.forEach(function (alert) {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 4000);
    }

    const chatContainer = document.getElementById('conversation');
    
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    const inputs = document.getElementsByTagName('input');
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type !== 'checkbox' && inputs[i].type !== 'radio') {
            inputs[i].classList.add('form-control');
        }
    }

    const selects = document.getElementsByTagName('select');
    for (let i = 0; i < selects.length; i++) {
        selects[i].classList.add('form-select');
    }

    const textareas = document.getElementsByTagName('textarea');
    for (let i = 0; i < textareas.length; i++) {
        textareas[i].classList.add('form-control');
        if (!textareas[i].rows) {
            textareas[i].rows = 5;
        }
    }
});