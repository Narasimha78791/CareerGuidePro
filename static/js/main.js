document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Skills extraction from text input
    const skillsInput = document.getElementById('skills');
    const skillsExtractBtn = document.getElementById('extract-skills');
    const skillsSuggestions = document.getElementById('skills-suggestions');

    if (skillsInput && skillsExtractBtn && skillsSuggestions) {
        skillsExtractBtn.addEventListener('click', function() {
            const text = skillsInput.value;
            if (text.trim().length < 10) {
                alert('Please enter more text about your skills to analyze');
                return;
            }

            fetch('/api/extract-skills', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.skills && data.skills.length > 0) {
                    skillsSuggestions.innerHTML = '';
                    data.skills.forEach(skill => {
                        const badge = document.createElement('span');
                        badge.className = 'badge bg-info me-2 mb-2';
                        badge.textContent = skill;
                        badge.style.cursor = 'pointer';
                        badge.addEventListener('click', function() {
                            // Add the skill to the skills input if not already included
                            const currentSkills = skillsInput.value.toLowerCase();
                            if (!currentSkills.includes(skill.toLowerCase())) {
                                skillsInput.value = currentSkills ? `${currentSkills}, ${skill}` : skill;
                            }
                        });
                        skillsSuggestions.appendChild(badge);
                    });
                    skillsSuggestions.style.display = 'block';
                } else {
                    skillsSuggestions.innerHTML = '<p class="text-muted">No specific skills identified. Try adding more details about your technical abilities.</p>';
                    skillsSuggestions.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error extracting skills:', error);
                skillsSuggestions.innerHTML = '<p class="text-danger">Error processing your skills. Please try again.</p>';
                skillsSuggestions.style.display = 'block';
            });
        });
    }

    // Star rating system for feedback
    const ratingStars = document.querySelectorAll('.rating-stars i');
    const ratingInput = document.getElementById('rating');
    
    if (ratingStars.length > 0 && ratingInput) {
        // Set initial rating if exists
        const initialRating = ratingInput.value;
        if (initialRating) {
            updateStars(initialRating);
        }
        
        ratingStars.forEach((star, index) => {
            // Mouse hover effect
            star.addEventListener('mouseover', () => {
                updateStars(index + 1);
            });
            
            // Click to set rating
            star.addEventListener('click', () => {
                ratingInput.value = index + 1;
                updateStars(index + 1);
            });
        });
        
        // Mouse leave - revert to current rating
        document.querySelector('.rating-stars').addEventListener('mouseleave', () => {
            updateStars(ratingInput.value || 0);
        });
        
        function updateStars(count) {
            ratingStars.forEach((star, index) => {
                if (index < count) {
                    star.classList.remove('far');
                    star.classList.add('fas');
                } else {
                    star.classList.remove('fas');
                    star.classList.add('far');
                }
            });
        }
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
});
