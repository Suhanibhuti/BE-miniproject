
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
function saveTimes() {
  // Get the values from the time selectors
  var start_hour = document.getElementById('start_hour').value;
  var start_minute = document.getElementById('start_minute').value;
  var start_ampm = document.getElementById('start_ampm').value;
  var start_slot = document.getElementById('start_slot').value;

  var end_hour = document.getElementById('end_hour').value;
  var end_minute = document.getElementById('end_minute').value;
  var end_ampm = document.getElementById('end_ampm').value;
  var end_slot = document.getElementById('end_slot').value;

  // Combine the values to form the full time strings
  var start_time = `${start_hour}:${start_minute} ${start_ampm} (${start_slot})`;
  var end_time = `${end_hour}:${end_minute} ${end_ampm} (${end_slot})`;

  // Display the new start time
  var startList = document.getElementById('previous_start_times');
  if (startList.children[0].innerText === 'None') {
    startList.innerHTML = '';
  }
  var startItem = document.createElement('li');
  startItem.innerText = start_time;
  startList.appendChild(startItem);

  // Display the new end time
  var endList = document.getElementById('previous_end_times');
  if (endList.children[0].innerText === 'None') {
    endList.innerHTML = '';
  }
  var endItem = document.createElement('li');
  endItem.innerText = end_time;
  endList.appendChild(endItem);
}

//  new time script
function addTiming() {
  const startTime = document.getElementById('start-time').value;
  const endTime = document.getElementById('end-time').value;

  if (startTime && endTime) {
      const timingList = document.getElementById('timing-list');
      const newTiming = document.createElement('li');
      newTiming.textContent = `${startTime} - ${endTime}`;
      timingList.appendChild(newTiming);

      alert('Timing added successfully!');
  } else {
      alert('Please enter both start and end times.');
  }
}
