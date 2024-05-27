// so_well/static/js/print.js
// Function to format date as MM/DD/YYYY
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00Z');  // Treat as UTC
    return `${date.getUTCMonth() + 1}/${date.getUTCDate()}/${date.getUTCFullYear()}`;
}

// Function to format Voter ID
function formatVoterId(voterId) {
    if (!voterId) return '';
    return voterId.slice(0, 3) + '-' + voterId.slice(3, 6) + '-' + voterId.slice(6);
}

// Function to capitalize first and last name, even if in all caps
function capitalizeName(name) {
    if (!name) return '';
    name = name.toLowerCase();
    return name.replace(/\b\w/g, char => char.toUpperCase());
}

function generateSheet() {
    const sheetNumber = document.getElementById('sheet-number-input').value;
    if (!sheetNumber) {
        alert('Please enter a valid sheet number');
        return;
    }
    document.getElementById('sheet-number').textContent = sheetNumber;
    document.getElementById('footer-sheet-number').textContent = sheetNumber;

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
        .then(response => {
            const { data, sheet_info } = response;

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
                    formatVoterId(entry.voterId || ''),
                    capitalizeName(entry.firstName || ''),
                    capitalizeName(entry.lastName || ''),
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
                    // Center specific columns
                    if ([7, 8, 9, 10].includes(j)) {
                        cell.className = 'center';
                    }
                    // Align Apt# and City to the left
                    if ([5, 6].includes(j)) {
                        cell.className = 'left';
                    }
                    row.appendChild(cell);
                });

                dataRows.appendChild(row);
            }

            // Set circulator information
            const circulatorInfo = `
                ${sheet_info.circulator_name || ''}<br>
                ${sheet_info.circulator_address_1 || ''}<br>
                ${sheet_info.circulator_address_2 || ''}<br>
                ${sheet_info.circulator_city || ''}, ${sheet_info.circulator_state || ''} ${sheet_info.circulator_zip || ''}
            `;
            document.getElementById('circulator-info').innerHTML = circulatorInfo;

            // Set notary information
            const notaryInfo = `
                <strong>Name:</strong> ${sheet_info.notary_name || ''}<br>
                <strong>Registration:</strong> ${sheet_info.notary_registration || ''}<br>
                <strong>Expiration:</strong> ${formatDate(sheet_info.notary_expiration) || ''}<br>
                <strong>State:</strong> ${sheet_info.notary_state || ''}
            `;
            document.getElementById('notary-info').innerHTML = notaryInfo;

            // Set notarized date
            document.getElementById('notarize-date').textContent = formatDate(sheet_info.notarized_on);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('Failed to fetch data for the given sheet number.');
        });
}

// Event listener for Enter key on sheet number input
document.getElementById('sheet-number-input').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        generateSheet();
    }
});
