// so_well/static/js/sheets.js
document.addEventListener('DOMContentLoaded', function() {
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

    function showNotification(elementId, message, type) {
        const notification = document.getElementById(elementId);
        notification.style.display = 'block';
        notification.className = 'alert alert-' + type;
        notification.innerHTML = message;
        setTimeout(() => {
            notification.style.display = 'none';
        }, 5000);
    }

    document.getElementById('distribute-status').addEventListener('click', async function() {
        const sheetNumber = document.getElementById('distribute-sheet-number').value;
        const response = await fetch('/sheets/update_sheet_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sheet_number: sheetNumber, new_status: 'Signing' })
        });

        const data = await response.json();
        const message = data.success ? `Sheet ${sheetNumber} transitioned to Signing` : (data.error || 'Failed to update sheet status');
        const type = data.success ? 'success' : 'danger';
        showNotification('distribute-notification', message, type);
    });

    document.getElementById('intake-status').addEventListener('click', async function() {
        const sheetNumber = document.getElementById('intake-sheet-number').value;
        const response = await fetch('/sheets/update_sheet_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sheet_number: sheetNumber, new_status: 'Summarizing' })
        });

        const data = await response.json();
        const message = data.success ? `Sheet ${sheetNumber} transitioned to Summarizing` : (data.error || 'Failed to update sheet status');
        const type = data.success ? 'success' : 'danger';
        showNotification('intake-notification', message, type);
    });

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
    });
});
