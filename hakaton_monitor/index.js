const loginOverlay = document.getElementById('login-overlay');
  const registerOverlay = document.getElementById('register-overlay');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const openRegisterBtn = document.getElementById('open-register');

  // Переключение на регистрацию
  openRegisterBtn.addEventListener('click', () => {
    loginOverlay.style.display = 'none';
    registerOverlay.style.display = 'flex';
  });

  // Логин: закрываем только после успешной валидации
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (loginForm.checkValidity()) {
      // fetch('/api/login', { method: 'POST', body: new FormData(loginForm) })
      // .then(() => { /* токен получен */ })
      
      loginOverlay.style.display = 'none';  // закрываем
      document.documentElement.style.overflow = 'auto';
      document.body.style.overflow = 'auto';
    } else {
      loginForm.reportValidity();
    }
  });

  // Регистрация: проверяем совпадение паролей + валидация
  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const password = registerForm.password.value;
    const confirmPassword = registerForm['confirm-password'].value;
    
    if (password !== confirmPassword) {
      alert('Пароли не совпадают!');
      return;
    }
    
    if (registerForm.checkValidity()) {
      // fetch('/api/register', { method: 'POST', body: new FormData(registerForm) })
      
      registerOverlay.style.display = 'none';
      document.documentElement.style.overflow = 'auto';
      document.body.style.overflow = 'auto';
    } else {
      registerForm.reportValidity();
    }
  })
  
  document.getElementById('back-to-login').addEventListener('click', () => {
  registerOverlay.style.display = 'none';
  loginOverlay.style.display = 'flex';
});;