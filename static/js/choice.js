function submitChoice(selectedImage) {
    const selectedInput = document.getElementById('selected-image');
    const choiceForm = document.getElementById('choice-form');
    const patientCards = document.querySelectorAll('.patient-card');

    if (selectedInput && choiceForm) {
        patientCards.forEach(card => {
            const cardImage = card.querySelector('img');
            if (cardImage.src.includes(selectedImage)) {
                card.classList.add('selected');
                cardImage.style.opacity = '1';
            } else {
                cardImage.style.opacity = '0.5';
            }
        });

        selectedInput.value = selectedImage;
        
        const formData = new FormData(choiceForm);
        fetch(choiceForm.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.show_reconsider) {
                showReconsiderModal(data);
            } else {
                // No reconsider needed, reload page to go to the next choice
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}



function moveDoctor(direction) {
    const doctor = document.getElementById('draggableDoctor');
    const patients = document.querySelectorAll('.patient-card');
    const target = direction === 'left' ? patients[0] : patients[1];
    
    const targetRect = target.getBoundingClientRect();
    const doctorRect = doctor.getBoundingClientRect();
    
    const moveX = targetRect.left + (targetRect.width/2) - doctorRect.left - (doctorRect.width/2);
    const moveY = targetRect.top + (targetRect.height/2) - doctorRect.top - (doctorRect.height/2);

    doctor.style.transform = `translate(${moveX}px, ${moveY}px)`;
    
    setTimeout(() => {
        const patientImage = target.querySelector('.patient-image');
        submitChoice(patientImage.dataset.filename);
    }, 600);
}

function initDraggableDoctor() {
    const doctor = document.getElementById('draggableDoctor');
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    doctor.addEventListener('mousedown', startDragging);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDragging);

    function startDragging(e) {
        initialX = e.clientX - doctor.offsetLeft;
        initialY = e.clientY - doctor.offsetTop;
        isDragging = true;
        doctor.style.transition = 'none';
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            doctor.style.transform = `translate(${currentX}px, ${currentY}px)`;
            checkOverlap();
        }
    }

    function stopDragging() {
        if (isDragging) {
            isDragging = false;
            doctor.style.transition = 'transform 0.3s ease';
        }
    }

    function checkOverlap() {
        const doctorRect = doctor.getBoundingClientRect();
        const patients = document.querySelectorAll('.patient-card');
        
        patients.forEach(patient => {
            const patientRect = patient.getBoundingClientRect();
            if (isOverlapping(doctorRect, patientRect)) {
                const patientImage = patient.querySelector('.patient-image');
                submitChoice(patientImage.dataset.filename);
            }
        });
    }

    function isOverlapping(rect1, rect2) {
        return !(rect1.right < rect2.left || 
                rect1.left > rect2.right || 
                rect1.bottom < rect2.top || 
                rect1.top > rect2.bottom);
    }
}

function showReconsiderModal(data) {
    const modal = document.getElementById('reconsider-modal');
    const originalChoice = document.getElementById('original-choice');
    const suggestedChoice = document.getElementById('suggested-choice');
    const originalDesc = document.getElementById('original-choice-description');
    const suggestedDesc = document.getElementById('suggested-choice-description');
    
    originalChoice.src = `/static/${data.original}`;
    suggestedChoice.src = `/static/${data.suggestion}`;
    originalDesc.textContent = data.original_desc;
    suggestedDesc.textContent = data.suggestion_desc;
    
    modal.style.display = 'flex';
    setTimeout(() => modal.classList.add('active'), 10); // Allow CSS transition
}


function handleReconsider(change) {
    fetch('/reconsider', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            change_decision: change
        })
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            // Just hide the modal without reloading the page
            const modal = document.getElementById('reconsider-modal');
            modal.classList.remove('active');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300); // Short delay to allow transition to complete
            
            // Reset opacity of patient cards for new selection
            const patientCards = document.querySelectorAll('.patient-card');
            patientCards.forEach(card => {
                const cardImage = card.querySelector('img');
                cardImage.style.opacity = '1';
                card.classList.remove('selected');
            });
            
            // Optional: Show message to user to make final selection
            const instructionText = document.querySelector('.instruction-text p');
            if (instructionText) {
                instructionText.textContent = "Now please make your final selection for which patient to treat.";
                instructionText.style.fontWeight = "bold";
                instructionText.style.color = "#007bff";
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}





document.addEventListener('DOMContentLoaded', () => {
    initDraggableDoctor();
    
    const patients = document.querySelectorAll('.patient-card');
    patients.forEach((patient, index) => {
        setTimeout(() => {
            patient.style.opacity = '1';
        }, index * 500);
    });
    
    setTimeout(() => {
        document.getElementById('draggableDoctor').style.opacity = '1';
    }, 1000);
});
