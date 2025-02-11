function submitChoice(selectedImage) {
    const selectedInput = document.getElementById('selected-image');
    const choiceForm = document.getElementById('choice-form');
    const patientCards = document.querySelectorAll('.patient-card');

    if (selectedInput && choiceForm) {
        // Visual feedback for selection
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
        
        // Submit after brief visual feedback delay
        setTimeout(() => {
            choiceForm.submit();
        }, 300);
    }
}

// Initialize draggable doctor functionality
function initDraggableDoctor() {
    const doctorImage = document.querySelector('.doctor-image');
    const leftPatient = document.querySelector('.patient-card:first-child');
    const rightPatient = document.querySelector('.patient-card:last-child');
    
    let isDragging = false;
    let startX, startY;
    let originalX, originalY;

    function getTransformValues() {
        const transform = window.getComputedStyle(doctorImage).transform;
        const matrix = new DOMMatrix(transform);
        return {
            x: matrix.m41,
            y: matrix.m42
        };
    }

    function onMouseDown(e) {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        const transform = getTransformValues();
        originalX = transform.x;
        originalY = transform.y;
        doctorImage.style.cursor = 'grabbing';
    }

    function onMouseMove(e) {
        if (!isDragging) return;

        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        
        doctorImage.style.transform = `translate(${originalX + dx}px, ${originalY + dy}px)`;

        // Visual feedback
        const doctorRect = doctorImage.getBoundingClientRect();
        const leftRect = leftPatient.getBoundingClientRect();
        const rightRect = rightPatient.getBoundingClientRect();

        if (doctorRect.left < leftRect.right) {
            leftPatient.style.transform = 'scale(1.1)';
            rightPatient.style.transform = 'scale(1)';
        } else if (doctorRect.right > rightRect.left) {
            rightPatient.style.transform = 'scale(1.1)';
            leftPatient.style.transform = 'scale(1)';
        } else {
            leftPatient.style.transform = 'scale(1)';
            rightPatient.style.transform = 'scale(1)';
        }
    }

    function onMouseUp(e) {
        if (!isDragging) return;
        
        isDragging = false;
        doctorImage.style.cursor = 'grab';

        const doctorRect = doctorImage.getBoundingClientRect();
        const leftRect = leftPatient.getBoundingClientRect();
        const rightRect = rightPatient.getBoundingClientRect();

        // Reset patient card scales
        leftPatient.style.transform = 'scale(1)';
        rightPatient.style.transform = 'scale(1)';

        if (doctorRect.left < leftRect.right) {
            submitChoice(leftPatient.querySelector('.patient-image').dataset.filename);
        } else if (doctorRect.right > rightRect.left) {
            submitChoice(rightPatient.querySelector('.patient-image').dataset.filename);
        } else {
            // Return to center if not dropped on a patient
            doctorImage.style.transform = 'translate(0, 0)';
        }
    }

    doctorImage.addEventListener('mousedown', onMouseDown);
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
}

document.addEventListener('DOMContentLoaded', () => {
    initDraggableDoctor();
});
