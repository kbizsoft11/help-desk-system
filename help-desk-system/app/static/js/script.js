document.addEventListener("DOMContentLoaded", () => {

    // Update Ticket Status
    document.querySelectorAll('select#status-dropdown').forEach(function (dropdown) {
        dropdown.addEventListener('change', function () {
            const newStatus = this.value;
            const ticketId = this.getAttribute('data-id');

            fetch(`/update_ticket_status/${ticketId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus })
            })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        alert('Failed to update status.');
                        throw new Error('Network response was not ok');
                    }
                })
                .then(data => {
                    alert('Updated successfully');
                    console.log(data.message);
                })
                .catch(error => console.error('Error:', error));
        });
    });

    //Confirm Delete Ticket Admin
    document.querySelectorAll('form.admin-delete-ticket').forEach(function (form) {

        form.addEventListener("submit", function (e) {
            e.preventDefault();

            // Show confirmation dialog
            const confirmDelete = confirm("Do you really want to delete this ticket?");

            if (confirmDelete) {
                this.submit();
            } else {
                return;
            }
        })
    })

    // Confirm Delete Tickets
    document.querySelector('form#delete_all_users').addEventListener("submit", function (e) {
        e.preventDefault();  // Prevent the form from submitting immediately

        // Show confirmation dialog
        const confirmDelete = confirm("Do you really want to delete all tickets?");

        if (confirmDelete) {
            // If the user confirms, submit the form
            this.submit();  // This will submit the form
        } else {
            // If the user cancels, do nothing
            return;
        }
    });

    // // Function to set the selected value based on the URL query parameter
    // function setSelectValueFromURL() {
    //     const urlParams = new URLSearchParams(window.location.search);
    //     const status = urlParams.get('status'); // Get the 'status' query parameter

    //     console.log(status)

    //     if (status) {
    //         // Find the option with the matching value and set it as selected
    //         const selectElement = document.querySelector('select#status-dropdown-filter');
    //         selectElement.value = status; // Set the selected value based on the URL parameter
    //     }
    // }

    // // Call the function to set the initial value when the page loads
    // setSelectValueFromURL();

    // document.querySelector('select#status-dropdown-filter').addEventListener('change', function () {
    //     const selectedValue = this.value;

    //     // Get the current URL and update the query parameter with the selected value
    //     const currentUrl = window.location.href;
    //     const url = new URL(currentUrl);
    //     url.searchParams.set('status', selectedValue); // Add or update the 'status' query parameter

    //     // Redirect to the updated URL, which will reload the page with the new query parameter
    //     window.location.href = url.toString();
    // });


})