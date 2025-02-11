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
        setTimeout(() => {
            choiceForm.submit();
        }, 300);
    }
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
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            doctor.style.left = currentX + 'px';
            doctor.style.top = currentY + 'px';
            checkOverlap();
        }
    }

    function stopDragging() {
        isDragging = false;
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

document.addEventListener('DOMContentLoaded', initDraggableDoctor);
