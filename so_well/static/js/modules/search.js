// so_well/static/js/modules/search.js
import { updateFilterCounts } from './filterCounts.js';

export function searchVoters() {
    let formData = {
        'first_name': $('#first-name').val(),
        'middle_name': $('#middle-name').val(),
        'last_name': $('#last-name').val(),
        'house_number': $('#house-number').val(),
        'house_number_suffix': $('#house-number-suffix').val(),
        'street_name': $('#street-name').val(),
        'street_type': $('input.street-type-option:checked').map(function() { return this.value; }).get(),
        'direction': $('input.direction-option:checked').map(function() { return this.value; }).get(),
        'post_direction': $('input.post-direction-option:checked').map(function() { return this.value; }).get(),
        'apartment_number': $('#apartment-number').val(),
        'city': $('#city').val(),
        'state': $('#state').val(),
        'zip_code': $('#zip-code').val().substring(0, 5)  // Only take the first 5 characters for ZIP Code
    };

    console.log("Submitting search with formData:", formData);

    $.ajax({
        type: 'POST',
        url: '/advanced_search/',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(data) {
            console.log("Search results:", data);
            updateResultsTable(data.results);
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
        }
    });
}

function updateResultsTable(data) {
    let tbody = $('#results-table tbody');
    tbody.empty();
    if (data.length === 0) {
        tbody.append('<tr><td colspan="9" class="text-center">No results found</td></tr>');
    } else {
        data.forEach(function(voter) {
            // Combine address elements
            let address = `${voter.house_number} ${voter.house_number_suffix || ''} ${voter.direction || ''} ${voter.street_name} ${voter.street_type || ''} ${voter.post_direction || ''} ${voter.apartment_number ? 'Apt ' + voter.apartment_number : ''}`;
            let row = `<tr>
                <td>${voter.first_name}</td>
                <td>${voter.middle_name || ''}</td>
                <td>${voter.last_name}</td>
                <td>${address}</td>
                <td>${voter.city}</td>
                <td>${voter.state}</td>
                <td>${voter.zip_code}</td>
                <td>${voter.status}</td>
                <td><button class="btn btn-primary btn-match" data-voter='${JSON.stringify(voter)}'>Match</button></td>
            </tr>`;
            tbody.append(row);
        });
    }
}
