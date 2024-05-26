// so_well/static/js/print.js
// Function to format date as M/D/YY
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}/${String(date.getFullYear()).slice(-2)}`;
}

function generateSheet() {
    const sheetNumber = document.getElementById('sheet-number-input').value;
    if (!sheetNumber) {
        alert('Please enter a valid sheet number');
        return;
    }
    document.getElementById('sheet-number').textContent = sheetNumber;

    const fetchURL = `/fetch_data?sheet=${sheetNumber}`;
    console.log(`Fetching data from URL: ${fetchURL}`);

    // Fetch data from the backend
    fetch(fetchURL)
        .then(response => {
            if (!response.ok) {
                console.error('Network response was not ok', response);
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Clear existing rows
            const dataRows = document.getElementById('data-rows');
            dataRows.innerHTML = '';

            // Ensure 12 rows
            for (let i = 0; i < 12; i++) {
                const entry = data[i] || {};
                const row = document.createElement('tr');
                row.className = i % 2 === 0 ? 'even' : 'odd';  // Alternate row colors

                // Add cells with reordered columns
                const cells = [
                    i + 1,  // Row number
                    entry.voterId || '',
                    entry.firstName || '',
                    entry.lastName || '',
                    entry.address1 || '',
                    entry.address2 || '',
                    entry.city || '',
                    entry.state || '',
                    entry.zip || '',
                    formatDate(entry.dateSigned || ''),
                    entry.ssnLast4 || ''
                ];

                cells.forEach((cellData, j) => {
                    const cell = document.createElement('td');
                    cell.textContent = cellData;
                    // Style row number column
                    if (j === 0) {
                        cell.className = `row-number ${i % 2 === 0 ? 'row-number-even' : 'row-number-odd'}`;
                    }
                    row.appendChild(cell);
                });

                dataRows.appendChild(row);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('Failed to fetch data for the given sheet number.');
        });
}
