document.addEventListener('DOMContentLoaded', function() {

    // ПОява кнопки "Повернутися на початок"
    const backToTopButton = document.getElementById('backToTop');
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 70) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });
    
    // Плавна прокрутка до верху
    backToTopButton.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Сортування відгуків
    const filterButtons = document.querySelectorAll('.filter-buttons button');
    const testimonials = document.querySelectorAll('[data-category]');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                filterButtons.forEach(btn => {
                    btn.classList.remove('active', 'btn-primary');
                    btn.classList.add('btn-outline-primary');
                });
                this.classList.add('active', 'btn-primary');
                this.classList.remove('btn-outline-primary');
                
                const filter = this.getAttribute('data-filter');
                
                testimonials.forEach(testimonial => {
                    if (filter === 'all' || testimonial.getAttribute('data-category') === filter) {
                        testimonial.style.display = 'block';
                    } else {
                        testimonial.style.display = 'none';
                    }
                });
            });
    });
});
                    