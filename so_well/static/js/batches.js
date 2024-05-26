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

    document.querySelectorAll('.add-to-batch').forEach(button => {
        button.addEventListener('click', async function() {
            const sheetId = this.getAttribute('data-sheet-id');
            const response = await fetch('/batches/add_to_batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sheet_id: sheetId })
            });

            const data = await response.json();
            if (data.success) {
                showNotification(`Sheet ${sheetId} added to batch ${data.batch_id}`, 'success');
                this.disabled = true;
            } else {
                showNotification(data.error || 'Failed to add sheet to batch', 'danger');
            }
        });
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
