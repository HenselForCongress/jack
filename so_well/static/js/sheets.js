// so_well/static/js/sheets.js
document.addEventListener('DOMContentLoaded', function() {
    // Fetch notaries and circulators
    async function fetchOptions() {
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
    }

    fetchOptions();

    document.getElementById('update-status').addEventListener('click', async function() {
        const sheetNumber = document.getElementById('sheet-number').value;
        const newStatus = document.getElementById('new-status').value;

        const response = await fetch('/sheets/update_sheet_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sheet_number: sheetNumber, new_status: newStatus })
        });

        const data = await response.json();
        if (data.success) {
            alert('Sheet status updated');
        } else {
            alert('Failed to update sheet status');
        }
    });

    document.getElementById('close-sheet').addEventListener('click', async function() {
        const sheetId = document.getElementById('close-sheet-number').value;
        const notaryId = document.getElementById('notary-selector').value;
        const notarizedOn = document.getElementById('notarized-date').value;
        const collectorId = document.getElementById('circulator-selector').value;

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
        if (data.success) {
            alert('Sheet closed successfully');
        } else {
            alert('Failed to close sheet');
        }
    });
});
