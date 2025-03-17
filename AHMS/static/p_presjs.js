// Function to edit a schedule
function editSchedule() {
  // Get all schedule items
  const scheduleItems = document.querySelectorAll('.schedule-item');

  // Loop through each schedule item
  scheduleItems.forEach((item) => {
    // Get the medicine name, dosage, timing, and before/after food elements
    const medicineName = item.querySelector('span:nth-child(1)').textContent;
    const dosage = item.querySelector('span:nth-child(2)');
    const timing = item.querySelector('span:nth-child(3)');
    const beforeAfterFood = item.querySelector('select');

    // Add an edit button to each schedule item
    const editButton = document.createElement('button');
    editButton.textContent = 'Edit';
    editButton.classList.add('btn', 'btn-secondary');
    editButton.style.marginLeft = '10px';
    item.appendChild(editButton);

    // Add event listener to the edit button
    editButton.addEventListener('click', () => {
      // Prompt the user to enter new details
      const newDosage = prompt(`Enter new dosage for ${medicineName}:`, dosage.textContent);
      const newTiming = prompt(`Enter new timing for ${medicineName}:`, timing.textContent);
      const newBeforeAfterFood = prompt(`Enter new before/after food for ${medicineName}:`, beforeAfterFood.value);

      // Update the schedule details if the user provides input
      if (newDosage !== null && newTiming !== null && newBeforeAfterFood !== null) {
        dosage.textContent = newDosage;
        timing.textContent = newTiming;
        beforeAfterFood.value = newBeforeAfterFood;
        alert(`Schedule for ${medicineName} has been updated.`);
      } else {
        alert('Edit canceled. No changes were made.');
      }
    });
  });
}

// Function to handle the reminder toggle
document.addEventListener('DOMContentLoaded', () => {
  // Get all toggle switches
  const toggleSwitches = document.querySelectorAll('.toggle-switch');

  toggleSwitches.forEach((toggleSwitch, index) => {
      toggleSwitch.addEventListener('click', () => {
          toggleSwitch.classList.toggle('on');
          const isOn = toggleSwitch.classList.contains('on');
          console.log(`Reminder for group ${index + 1} is ${isOn ? 'ON' : 'OFF'}`);
      });
  });
});

// Call the editSchedule function when the page loads
document.addEventListener('DOMContentLoaded', editSchedule);