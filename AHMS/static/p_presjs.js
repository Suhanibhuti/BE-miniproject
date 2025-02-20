function editSchedule(schedules) {
  // Alert for starting the edit process
  alert('Starting the schedule edit process.');

  // Prompt user to enter the schedule they want to edit
  const scheduleName = prompt('Enter the name of the medicine to edit:');
  
  if (scheduleName) {
    // Check if the schedule exists
    if (schedules[scheduleName]) {
      // Prompt user to enter new details for the schedule
      const newDetails = prompt(`Enter new details for "${scheduleName}":`, schedules[scheduleName]);
      if (newDetails) {
        // Update the schedule
        schedules[scheduleName] = newDetails;
        alert(`Schedule "${scheduleName}" has been updated to: ${newDetails}`);
      } else {
        alert('Edit canceled. No new details provided.');
      }
    } else {
      alert(`Schedule "${scheduleName}" not found.`);
    }
  } else {
    alert('Edit canceled. No schedule name provided.');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const toggleSwitch = document.getElementById('toggleSwitch');
  const toggleLabel = document.getElementById('toggleLabel');

  if (toggleSwitch && toggleLabel) {
    toggleSwitch.addEventListener('click', () => {
      toggleSwitch.classList.toggle('on');
      const isOn = toggleSwitch.classList.contains('on');
      toggleLabel.textContent = isOn ? 'ON' : 'OFF';
      console.log(`Reminder is ${isOn ? 'ON' : 'OFF'}`);
    });
  } else {
    console.error('Toggle switch or label not found.');
  }
});
