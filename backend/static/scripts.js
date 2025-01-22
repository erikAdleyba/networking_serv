// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadCards();
});

// Создание карточки
document.getElementById('cardForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fullName = document.getElementById('fullName').value;
    const birthDate = document.getElementById('birthDate').value;
    const interests = document.getElementById('interests').value;

    if (birthDate && !isValidDate(birthDate)) {
        alert('Неверный формат даты. Используйте формат дд.мм.гггг.');
        return;
    }

    const response = await fetch('/cards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName, birth_date: birthDate, interests: interests })
    });

    if (response.ok) {
        alert('Карточка создана!');
        loadCards();
    }
});

// Загрузка карточек
async function loadCards() {
    const response = await fetch('/cards');
    const cards = await response.json();
    const cardsList = document.getElementById('cardsList');
    cardsList.innerHTML = cards.map(card => `
        <li class="list-group-item">
            <strong>${card[2]}</strong> (${card[3] || 'Не указана'}) - ${card[4] || 'Нет интересов'}
            <button class="btn btn-sm btn-warning float-end" onclick="openEditModal(${card[0]}, '${card[2]}', '${card[3] || ''}', '${card[4] || ''}')">Редактировать</button>
            <button class="btn btn-sm btn-danger float-end me-2" onclick="deleteCard(${card[0]})">Удалить</button>
        </li>
    `).join('');
}

// Удаление карточки
async function deleteCard(cardId) {
    const response = await fetch(`/cards/${cardId}`, { method: 'DELETE' });
    if (response.ok) {
        alert('Карточка удалена!');
        loadCards();
    }
}

// Валидация даты
function isValidDate(dateString) {
    const regex = /^\d{2}\.\d{2}\.\d{4}$/; // Формат дд.мм.гггг
    if (!regex.test(dateString)) return false;

    const [day, month, year] = dateString.split('.');
    const date = new Date(`${year}-${month}-${day}`);
    return date && date.getMonth() + 1 === parseInt(month);
}

// Открытие модального окна для редактирования
function openEditModal(cardId, fullName, birthDate, interests) {
    document.getElementById('editFullName').value = fullName;
    document.getElementById('editBirthDate').value = birthDate || '';
    document.getElementById('editInterests').value = interests || '';
    document.getElementById('editCardId').value = cardId;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}

// Сохранение изменений
document.getElementById('saveChangesBtn').addEventListener('click', async () => {
    const cardId = document.getElementById('editCardId').value;
    const fullName = document.getElementById('editFullName').value;
    const birthDate = document.getElementById('editBirthDate').value;
    const interests = document.getElementById('editInterests').value;

    if (birthDate && !isValidDate(birthDate)) {
        alert('Неверный формат даты. Используйте формат дд.мм.гггг.');
        return;
    }

    const response = await fetch(`/cards/${cardId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName, birth_date: birthDate, interests: interests })
    });

    if (response.ok) {
        alert('Карточка обновлена!');
        loadCards();
        bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
    }
});