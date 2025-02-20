// Add event listener to handle form submission
document.getElementById('patientForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Gather form data
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    // Validate consent checkbox
    if (!formData.get('consent')) {
        alert('Please provide your consent to submit the form.');
        return;
    }

    // Display submitted data for testing (you can replace this with an API call)
    console.log('Submitted Data:', data);

    // Show success message
    alert('Patient details submitted successfully!');

    // Reset the form
    this.reset();
});
