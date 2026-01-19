document.addEventListener('DOMContentLoaded', function() {
    const selector = document.getElementById('id_participants_selector');
    const customInput = document.getElementById('id_custom_participants');
    if (selector && customInput) {
        function toggleCustomInput() {
            if (selector.value === 'custom') {
                customInput.style.display = 'inline-block';
                customInput.required = true;
            } else {
                customInput.style.display = 'none';
                customInput.required = false;
            }
        }
        toggleCustomInput();
        selector.addEventListener('change', toggleCustomInput);
    }
});