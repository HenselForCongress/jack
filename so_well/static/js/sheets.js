// so_well/static/js/sheets.js
document.addEventListener('DOMContentLoaded', function() {
    // Fetch notaries and circulators
    async function fetchOptions() {
        try {
            const notaryResp = await fetch('/sheets/notaries');
            const circulatorResp = await fetch('/sheets/circulators');

            const notaries = await notaryResp.json();
            const circulators = await circulatorResp.json();

            notaries.forEach(notary => {
                const option = document.createElement('option');
                option.value = notary.id;
                option.text = notary.full_name;
                document.getElementById('notary-selector').add(option);
            });

            circulators.forEach(circulator => {
                const option = document.createElement('option');
                option.value = circulator.id;
                option.text = circulator.full_name;
                document.getElementById('circulator-selector').add(option);
            });
        } catch (error) {
            console.error('Error fetching options:', error);
        }
    }

    fetchOptions();

    // Function to show notifications
    function showNotification(elementId, message, type) {
        const notification = document.getElementById(elementId);
        notification.style.display = 'block';
        notification.className = 'alert alert-' + type;
        notification.innerHTML = message;
        setTimeout(() => {
            notification.style.display = 'none';
        }, 5000);
    }

    // Function to reset a field and focus on it
    function resetFieldAndFocus(inputId) {
        const inputElement = document.getElementById(inputId);
        inputElement.value = '';
        inputElement.focus();
    }

    // Function to update the sheet status
    async function updateStatus(endpoint, sheetNumber, newStatus, notificationId, buttonId) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sheet_number: sheetNumber, new_status: newStatus })
        });

        const data = await response.json();
        const message = data.success ? `Sheet ${sheetNumber} transitioned to ${newStatus}` : (data.error || 'Failed to update sheet status');
        const type = data.success ? 'success' : 'danger';
        showNotification(notificationId, message, type);

        if (data.success) {
            resetFieldAndFocus(buttonId);
        }
    }

    // Attach event listeners to buttons
    document.getElementById('distribute-status').addEventListener('click', function() {
        const sheetNumber = document.getElementById('distribute-sheet-number').value;
        updateStatus('/sheets/update_sheet_status', sheetNumber, 'Signing', 'distribute-notification', 'distribute-sheet-number');
    });

    document.getElementById('intake-status').addEventListener('click', function() {
        const sheetNumber = document.getElementById('intake-sheet-number').value;
        updateStatus('/sheets/update_sheet_status', sheetNumber, 'Summarizing', 'intake-notification', 'intake-sheet-number');
    });

    // Modified close-sheet functionality to only reset the sheet number field
    document.getElementById('close-sheet').addEventListener('click', async function() {
        const sheetId = document.getElementById('close-sheet-number').value;
        const notaryId = document.getElementById('notary-selector').value;
        const notarizedOn = document.getElementById('notarized-date').value;
        const collectorId = document.getElementById('circulator-selector').value;

        // Ensure none of the necessary values are empty
        if (!sheetId || !notaryId || !notarizedOn || !collectorId) {
            showNotification('close-notification', 'All fields are required to close a sheet', 'danger');
            return;
        }

        const response = await fetch('/sheets/close_sheet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sheet_id: sheetId,
                notary_id: notaryId,
                notarized_on: notarizedOn,
                collector_id: collectorId
            })
        });

        const data = await response.json();
        const message = data.success ? `Sheet ${sheetId} closed successfully` : (data.error || 'Failed to close sheet');
        const type = data.success ? 'warning' : 'danger';
        showNotification('close-notification', message, type);

        if (data.success) {
            // Only reset the sheet number field and focus on it
            resetFieldAndFocus('close-sheet-number');
        }
    });

    // Add event listeners for Enter key
    ['#distribute-sheet-number', '#intake-sheet-number', '#close-sheet-number'].forEach(selector => {
        document.querySelector(selector).addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const buttonId = selector === '#distribute-sheet-number' ? 'distribute-status' :
                                 selector === '#intake-sheet-number' ? 'intake-status' : 'close-sheet';
                document.getElementById(buttonId).click();
            }
        });
    });
});
