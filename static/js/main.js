document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(message => {
        // Set a timeout to fade out and then remove the message
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.marginBottom = '0';
            message.style.paddingTop = '0';
            message.style.paddingBottom = '0';
            message.style.height = '0';
            message.style.overflow = 'hidden';

            // Remove from DOM entirely after transition completes
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
});
