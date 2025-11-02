/* SunBot Robotics Official Website - Main JavaScript */

// ===== Language Toggle =====
let currentLang = 'en';

const translations = {
    en: {
        nav: {
            home: 'Home',
            about: 'About',
            courses: 'Courses',
            gallery: 'Gallery',
            fll: 'FLL',
            contact: 'Contact'
        },
        hero: {
            title: 'Welcome to SunBot Robotics',
            subtitle: 'Inspiring Young Minds Through STEM Education',
            cta: 'Explore Our Courses'
        },
        about: {
            title: 'About SunBot Robotics',
            content: 'SunBot Robotics is dedicated to providing high-quality STEM education for children aged 5-15. Our mission is to inspire creativity, foster problem-solving skills, and prepare the next generation of innovators through hands-on robotics and coding programs.'
        },
        courses: {
            title: 'Our Courses',
            viewDetails: 'View Details'
        },
        gallery: {
            title: 'Student Gallery'
        },
        footer: {
            copyright: '© 2025 SunBot Robotics | Edmonton, Canada'
        }
    },
    zh: {
        nav: {
            home: '首页',
            about: '关于我们',
            courses: '课程',
            gallery: '相册',
            fll: 'FLL竞赛',
            contact: '联系我们'
        },
        hero: {
            title: '欢迎来到 SunBot Robotics',
            subtitle: '通过STEM教育激发年轻思维',
            cta: '探索我们的课程'
        },
        about: {
            title: '关于 SunBot Robotics',
            content: 'SunBot Robotics致力于为5-15岁儿童提供高质量的STEM教育。我们的使命是通过实践性的机器人和编程课程，激发创造力，培养解决问题的能力，并为下一代创新者做好准备。'
        },
        courses: {
            title: '我们的课程',
            viewDetails: '查看详情'
        },
        gallery: {
            title: '学生相册'
        },
        footer: {
            copyright: '© 2025 SunBot Robotics | 加拿大埃德蒙顿'
        }
    }
};

function updateLanguage(lang) {
    currentLang = lang;
    const t = translations[lang];
    
    // Update navigation
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const keys = key.split('.');
        let value = t;
        for (const k of keys) {
            value = value[k];
        }
        if (value) {
            element.textContent = value;
        }
    });
    
    // Update active language button
    document.querySelectorAll('.lang-toggle button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });
    
    // Store preference
    localStorage.setItem('preferredLang', lang);
}

// Initialize language
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('preferredLang') || 'en';
    updateLanguage(savedLang);
    
    // Set up language toggle buttons
    document.querySelectorAll('.lang-toggle button').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            updateLanguage(lang);
        });
    });
});

// ===== Lightbox Functionality =====
let currentImageIndex = 0;
let galleryImages = [];

function initLightbox() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    galleryImages = Array.from(galleryItems).map(item => item.querySelector('img').src);
    
    galleryItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            openLightbox(index);
        });
    });
}

function openLightbox(index) {
    currentImageIndex = index;
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    
    if (lightbox && lightboxImg) {
        lightboxImg.src = galleryImages[index];
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function navigateLightbox(direction) {
    if (direction === 'next') {
        currentImageIndex = (currentImageIndex + 1) % galleryImages.length;
    } else {
        currentImageIndex = (currentImageIndex - 1 + galleryImages.length) % galleryImages.length;
    }
    document.getElementById('lightbox-img').src = galleryImages[currentImageIndex];
}

// Initialize lightbox when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initLightbox();
    
    // Close lightbox handlers
    const lightboxClose = document.getElementById('lightbox-close');
    if (lightboxClose) {
        lightboxClose.addEventListener('click', closeLightbox);
    }
    
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        const lightbox = document.getElementById('lightbox');
        if (lightbox && lightbox.classList.contains('active')) {
            if (e.key === 'Escape') {
                closeLightbox();
            } else if (e.key === 'ArrowRight') {
                navigateLightbox('next');
            } else if (e.key === 'ArrowLeft') {
                navigateLightbox('prev');
            }
        }
    });
    
    // Lightbox navigation buttons
    const lightboxPrev = document.getElementById('lightbox-prev');
    const lightboxNext = document.getElementById('lightbox-next');
    
    if (lightboxPrev) {
        lightboxPrev.addEventListener('click', (e) => {
            e.stopPropagation();
            navigateLightbox('prev');
        });
    }
    
    if (lightboxNext) {
        lightboxNext.addEventListener('click', (e) => {
            e.stopPropagation();
            navigateLightbox('next');
        });
    }
});

// ===== Contact Form Handling =====
function handleContactForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Basic validation
    if (!data.name || !data.email || !data.message) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        alert('Please enter a valid email address.');
        return;
    }
    
    // Create mailto link
    const subject = encodeURIComponent(`Contact from ${data.name} - ${data.course || 'General Inquiry'}`);
    const body = encodeURIComponent(`
Name: ${data.name}
Email: ${data.email}
Interested Course: ${data.course || 'General Inquiry'}

Message:
${data.message}
    `);
    
    window.location.href = `mailto:sunbotcanada@gmail.com?subject=${subject}&body=${body}`;
    
    // Reset form
    form.reset();
    
    // Show success message
    alert('Thank you for your message! Your email client will open shortly.');
}

// Initialize contact form
document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactForm);
    }
});

// ===== Smooth Scroll =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== Navbar Active State =====
function updateActiveNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', updateActiveNav);

// ===== Scroll to Top Button =====
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.innerHTML = '↑';
    button.className = 'scroll-to-top';
    button.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background-color: var(--primary-yellow);
        color: var(--primary-blue);
        border: none;
        border-radius: 50%;
        font-size: 1.5rem;
        cursor: pointer;
        display: none;
        z-index: 1000;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    `;
    
    button.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    });
    
    document.body.appendChild(button);
}

document.addEventListener('DOMContentLoaded', createScrollToTopButton);

// ===== Mobile Menu Toggle (for Bootstrap) =====
// This will work with Bootstrap's collapse functionality
document.addEventListener('DOMContentLoaded', () => {
    // Close mobile menu when clicking a link
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        });
    });
});

