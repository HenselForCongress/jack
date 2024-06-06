// so_well/static/js/entry.js

$(document).ready(function () {
    console.log("Document ready - initializing");

    fetchStateOptions();
    fetchDirectionOptions();
    fetchStreetTypeOptions();

    // Prepopulate the date fields with the current date, but do not set the Day value
    prepopulateDateFields();

    // Handle form submission and search
    $('#search-form').on('submit', function (e) {
        e.preventDefault();
        console.log("Search form submitted");
        searchVoters(); // Trigger search
    });

    $('#not-found').on('click', function () {
        console.log("Not Found clicked");
        $('#not-found-modal').modal('show');
        // Set focus to the first field when the not-found modal opens
        $('#nf-row-number').focus();

        // Auto-fill modal sheet number and date
        $('#nf-sheet-number').val($('#header-sheet-number').val());

        let month = $('#header-month').val();
        let day = $('#header-day').val() || '01'; // Use '01' if day is empty
        let year = $('#header-year').val();
        let dateSigned = null;

        if (month && day && year) {
            dateSigned = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        } else if (month && year) {
            dateSigned = `${year}-${month.padStart(2, '0')}-01`;
        } else if (year) {
            dateSigned = `${year}-01-01`;
        }

        $('#nf-date-signed').val(dateSigned);

        // Hide middle name field
        $('#nf-middle-name').closest('.form-group').hide();

        // Fetch the next available row number
        fetchNextAvailableRowNumber($('#nf-sheet-number').val(), '#nf-row-number');
    });

    $('#results-table').on('click', '.btn-match', function () {
        let voterData = $(this).data('voter');
        console.log("Match button clicked", voterData);
        $('#match-modal').data('voter', voterData).modal('show');

        // Auto-fill modal sheet number
        $('#sheet-number').val($('#header-sheet-number').val());

        // Pre-populate the date-collected field
        let month = $('#header-month').val();
        let day = $('#header-day').val() || '01'; // Use '01' if day is empty
        let year = $('#header-year').val();
        let collectedDate = null;

        if (month && day && year) {
            collectedDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        } else if (month && year) {
            collectedDate = `${year}-${month.padStart(2, '0')}-01`;
        } else if (year) {
            collectedDate = `${year}-01-01`;
        }

        $('#date-collected').val(collectedDate);

        // Fetch the next available row number
        fetchNextAvailableRowNumber($('#sheet-number').val(), '#row-number');
    });

    $('#match-modal').on('show.bs.modal', function () {
        const sheetNumber = $('#header-sheet-number').val();
        // Fetch the next available row number
        fetchNextAvailableRowNumber(sheetNumber, '#row-number');
    });

    $('#match-form').on('submit', function (e) {
        e.preventDefault();
        if (validateMatchForm()) {
            submitMatchForm();
        }
    });

    // Listen for the Enter key on the match modal and trigger submit
    $('#match-modal').keypress(function(e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            if (validateMatchForm()) {
                submitMatchForm();
            }
        }
    });

    function validateMatchForm() {
        let isValid = true;
        $('#match-form').find('input[required]').each(function() {
            if ($(this).val() === '') {
                isValid = false;
                return false; // Exit each loop
            }
        });
        return isValid;
    }

    function submitMatchForm() {
        let voterData = $('#match-modal').data('voter');
        let formData = {
            sheet_number: $('#sheet-number').val(),
            row_number: $('#row-number').val(),
            date_collected: $('#date-collected').val(),
            last_four_ssn: $('#last-4').val(),
            voter_id: voterData.voter_id
        };
        console.log("Match form submitted", formData);
        $.ajax({
            type: 'POST',
            url: '/signatures/verify',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                console.log("Match recorded successfully");
                $('#match-modal').modal('hide');
                showNotification('Successfully recorded!', 'success');
                resetFormFields(); // Clear the form fields after successful submission

                // Automatically focus on "First Name" field
                $('#first-name').focus();
            },
            error: function(xhr, status, error) {
                console.error('Error recording match:', error);
            }
        });
    }

    $('#not-found-form').on('submit', function (e) {
        e.preventDefault();
        let formData = {
            sheet_number: $('#nf-sheet-number').val(),
            row_number: $('#nf-row-number').val(),
            date_collected: $('#nf-date-signed').val(),
            first_name: $('#nf-first-name').val(),
            last_name: $('#nf-last-name').val(),
            address: $('#nf-address').val(),
            apartment_number: $('#nf-apartment-number').val(),
            city: $('#nf-city').val(),
            state: $('#nf-state').val(),
            zip_code: $('#nf-zip-code').val(),
            last_four_ssn: $('#nf-last-4').val()
        };

        console.log("Submitting Not Found form with formData:", formData);

        $.ajax({
            type: 'POST',
            url: '/signatures/verify',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (data) {
                console.log("Not Found recorded successfully");
                $('#not-found-modal').modal('hide');
                showNotification('Successfully recorded!', 'success');
                resetNotFoundFormFields(); // Clear the form fields after successful submission

                // Automatically focus on "First Name" field on the main form
                $('#first-name').focus();
            },
            error: function (xhr, status, error) {
                console.error('Error recording Not Found:', error);
                showNotification(`Error: ${xhr.responseJSON.error}`, 'danger');
            }
        });
    });

    // Event handler for form submission using Enter key on the Not Found modal
    $('#not-found-modal').keypress(function(e) {
        if (e.which === 13) { // Enter key
            $('#not-found-form').submit();
        }
    });

    function fetchNextAvailableRowNumber(sheetNumber, rowNumberSelector) {
        if (sheetNumber) {
            $.ajax({
                type: 'GET',
                url: '/sheets/get_all_row_numbers',
                data: { sheet_id: sheetNumber },
                success: function (response) {
                    let rowNumbers = response.row_numbers;
                    let nextAvailableRow = getNextAvailableRowNumber(rowNumbers);
                    $(rowNumberSelector).val(nextAvailableRow);
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching row numbers:', error);
                    $(rowNumberSelector).val(1); // Default to 1 if there's an error.
                }
            });
        } else {
            $(rowNumberSelector).val(1); // Default to 1 if no sheet number is set.
        }
    }

    function getNextAvailableRowNumber(rowNumbers) {
        if (rowNumbers.length === 0) {
            return 1;
        }

        let highestOccupiedRow = Math.max(...rowNumbers);
        for (let i = highestOccupiedRow + 1; i <= 12; i++) {
            if (!rowNumbers.includes(i)) {
                return i;
            }
        }
        for (let i = 1; i <= 12; i++) {
            if (!rowNumbers.includes(i)) {
                return i;
            }
        }
        return 1; // Fallback to 1 if all rows are taken.
    }

    function fetchStateOptions() {
        console.log("Fetching state options");
        $.ajax({
            url: '/advanced_search/states',
            method: 'GET',
            success: function (data) {
                console.log('States data:', data);
                data.forEach(function (state) {
                    $('#state').append(`<option value="${state}">${state}</option>`);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching state options:', error);
            }
        });
    }

    function fetchDirectionOptions() {
        console.log("Fetching direction options");
        $.ajax({
            url: '/advanced_search/directions',
            method: 'GET',
            success: function (data) {
                console.log('Directions data:', data);
                data.directions.forEach(function (direction) {
                    $('#direction-options').append(`<div><input type="checkbox" class="direction-option" value="${direction.value}"> ${direction.value}</div>`);
                });
                data.post_directions.forEach(function (postDirection) {
                    $('#post-direction-options').append(`<div><input type="checkbox" class="post-direction-option" value="${postDirection.value}"> ${postDirection.value}</div>`);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching direction options:', error);
            }
        });
    }

    function fetchStreetTypeOptions() {
        console.log("Fetching street type options");
        $.ajax({
            url: '/advanced_search/street_types',
            method: 'GET',
            success: function (data) {
                console.log('Street Types data:', data);
                data.street_types.forEach(function (streetType) {
                    $('#street-type-options').append(`<div><input type="checkbox" class="street-type-option" value="${streetType.value}"> ${streetType.value}</div>`);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching street type options:', error);
            }
        });
    }

    function searchVoters() {
        let formData = {
            'first_name': $('#first-name').val(),
            'middle_name': $('#middle-name').val(),
            'last_name': $('#last-name').val(),
            'house_number': $('#house-number').val(),
            'house_number_suffix': $('#house-number-suffix').val(),
            'street_name': $('#street-name').val(),
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
                console.log("Search results received:", data);
                updateResultsTable(data.results);
            },
            error: function(xhr, status, error) {
                console.error('Error performing search:', error);
            }
        });
    }

    function updateResultsTable(results) {
        console.log("Updating results table with data:", results);

        let tbody = $('#results-table tbody');
        tbody.empty();

        if (results.length === 0) {
            tbody.append('<tr><td colspan="10" class="text-center">No results found</td></tr>');
        } else {
            results.forEach(function(voter) {
                let row = `<tr>
                    <td>${voter.first_name}</td>
                    <td>${voter.middle_name || ''}</td>
                    <td>${voter.last_name}</td>
                    <td>${voter.full_address}</td>
                    <td>${voter.apartment_number || ''}</td>
                    <td>${voter.city}</td>
                    <td>${voter.state}</td>
                    <td>${voter.zip_code}</td>
                    <td>${voter.status}</td>
                    <td class="last-row-number" style="display: none;">${voter.identification_number}</td>
                    <td><button class="btn btn-primary btn-match" data-voter='${JSON.stringify(voter)}'>Match</button></td>
                </tr>`;
                tbody.append(row);
            });

            // Focus on the first match button if there are 5 or fewer results
            if (results.length <= 5) {
                let matchButtons = $('button.btn-match');
                matchButtons.first().focus();

                // Make sure to allow tabbing through match buttons and then back to the first name field
                matchButtons.on('keydown', function (e) {
                    if (e.which === 9) { // Tab key
                        e.preventDefault();
                        let currentIndex = matchButtons.index(this);
                        if (e.shiftKey) {
                            // If Shift + Tab, move backwards
                            currentIndex = (currentIndex === 0) ? matchButtons.length : currentIndex;
                            matchButtons.eq(currentIndex - 1).focus();
                        } else {
                            // Move forward
                            currentIndex = (currentIndex === matchButtons.length - 1) ? -1 : currentIndex;
                            matchButtons.eq(currentIndex + 1).focus();
                        }
                    }
                });
            }
        }
    }

    function resetFormFields() {
        console.log("Resetting form fields");
        $('#search-form').trigger("reset");

        // Automatically focus on "First Name" field
        $('#first-name').focus();
    }

    function resetNotFoundFormFields() {
        console.log("Resetting not found form fields");
        $('#not-found-form').trigger("reset");
        $('#nf-sheet-number').val($('#header-sheet-number').val());
        $('#nf-date-signed').val($('#header-year').val() + '-' + $('#header-month').val().padStart(2, '0') + '-01');
    }

    function prepopulateDateFields() {
        let current_date = new Date();
        $('#header-month').val(('0' + (current_date.getMonth() + 1)).slice(-2));
        $('#header-day').val(''); // Leave Day empty
        $('#header-year').val(current_date.getFullYear());
    }

    function showNotification(message, type) {
        $('#notification').removeClass().addClass(`alert alert-${type}`).text(message).fadeIn();

        // Auto-hide notification after 3 seconds
        setTimeout(function() {
            $('#notification').fadeOut();
        }, 3000);
    }

    // Automatically focus on "First Name" field when document is ready
    $('#first-name').focus();

    // Prepopulate with default values on page load
    prepopulateDateFields();
});
