// so_well/static/js/batches.js
document.addEventListener('DOMContentLoaded', function() {
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    let selectedSheetId = null;

    document.querySelectorAll('.add-to-batch').forEach(button => {
        button.addEventListener('click', function() {
            selectedSheetId = this.getAttribute('data-sheet-id');
            $('#confirmationModal').modal('show');
        });
    });

    document.getElementById('confirmAddToBatch').addEventListener('click', async function() {
        const printedSummarySheet = document.getElementById('printedSummarySheet').checked;
        const photoOfBothSides = document.getElementById('photoOfBothSides').checked;

        if (!printedSummarySheet || !photoOfBothSides) {
            showNotification('Please confirm all required actions before adding to batch.', 'danger');
            return;
        }

        const response = await fetch('/batches/add_to_batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sheet_id: selectedSheetId })
        });

        const data = await response.json();
        if (data.success) {
            showNotification(`Sheet ${selectedSheetId} added to batch ${data.batch_id}`, 'success');
            $('#confirmationModal').modal('hide');
            setTimeout(function() {
                location.reload();
            }, 500);
        } else {
            showNotification(data.error || 'Failed to add sheet to batch', 'danger');
        }
    });

    document.getElementById('close-batch').addEventListener('click', async function() {
        const response = await fetch('/batches/close_batch', { method: 'POST' });

        const data = await response.json();
        if (data.success) {
            showNotification(`Batch ${data.batch_id} closed`, 'warning');
            document.getElementById('shipping-info').style.display = 'block';
        } else {
            showNotification(data.error || 'Failed to close the batch', 'danger');
        }
    });

    document.getElementById('confirm-shipment').addEventListener('click', async function() {
        const carrier = document.getElementById('carrier').value;
        const trackingNumber = document.getElementById('tracking-number').value;
        const shipDate = document.getElementById('ship-date').value;

        const response = await fetch('/batches/ship_batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ carrier, tracking_number: trackingNumber, ship_date: shipDate })
        });

        const data = await response.json();
        if (data.success) {
            showNotification(`Batch ${data.batch_id} shipped`, 'success');
        } else {
            showNotification(data.error || 'Failed to ship the batch', 'danger');
        }
    });
});
