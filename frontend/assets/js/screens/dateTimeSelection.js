import { stateManager } from '../state.js';

class DateSelectionScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        const today = new Date();
        let currentMonth = this.stateManager.getState('selectedCalendarMonth') !== undefined ? this.stateManager.getState('selectedCalendarMonth') : today.getMonth();
        let currentYear = this.stateManager.getState('selectedCalendarYear') !== undefined ? this.stateManager.getState('selectedCalendarYear') : today.getFullYear();
        const selectedDate = this.stateManager.getSelectedDate() ? new Date(this.stateManager.getSelectedDate()) : null;
        
        // Месяцы и дни недели
        const monthNames = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];
        const weekDays = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'];
        
        // Первый день месяца
        const firstDay = new Date(currentYear, currentMonth, 1);
        let startDay = firstDay.getDay();
        startDay = (startDay === 0) ? 6 : startDay - 1;
        
        let days = [];
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        
        for (let i = 0; i < startDay; i++) {
            days.push({
                day: '',
                date: null,
                other: true
            });
        }
        
        // Дни текущего месяца
        for (let i = 1; i <= daysInMonth; i++) {
            const dateObj = new Date(currentYear, currentMonth, i);
            days.push({
                day: i,
                date: dateObj,
                other: false
            });
        }
        
        // Дни следующего месяца (чтобы всегда было 6 строк по 7 дней)
        while (days.length < 42) {
            days.push({
                day: '',
                date: null,
                other: true
            });
        }
        
        // Формируем строки по 7 дней
        let rows = [];
        for (let i = 0; i < 6; i++) {
            rows.push(days.slice(i * 7, (i + 1) * 7));
        }
        
        return `
            <div class="calendar-header-row">
                <h2 class="section-title" style="margin:0;">Укажите дату поездки</h2>
            </div>
            <div class="calendar-quick-buttons">
                <button class="btn btn-secondary btn-quick-date" id="quickTodayBtn">Сегодня</button>
                <button class="btn btn-secondary btn-quick-date" id="quickTomorrowBtn">Завтра</button>
            </div>
            ${selectedDate ? `<div class="calendar-selected-info">Вы выбрали: ${selectedDate.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', weekday: 'short' })}</div>` : ''}
            <div class="card calendar-card">
                <div class="card-body calendar-body">
                    <div class="calendar-month-row" style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                        <button class="calendar-nav-btn" id="prevMonthBtn" aria-label="Предыдущий месяц" style="order:1;font-size:28px;color:#f65446;background:none;border:none;cursor:pointer;padding:4px 12px;line-height:1;display:flex;align-items:center;justify-content:center;"><span>&#8592;</span></button>
                        <div class="calendar-month-title" style="flex:1; text-align:center; order:2;">${monthNames[currentMonth]} ${currentYear}</div>
                        <button class="calendar-nav-btn" id="nextMonthBtn" aria-label="Следующий месяц" style="order:3;font-size:28px;color:#f65446;background:none;border:none;cursor:pointer;padding:4px 12px;line-height:1;display:flex;align-items:center;justify-content:center;"><span>&#8594;</span></button>
                    </div>
                    <table class="calendar-table">
                        <thead>
                            <tr>
                                ${weekDays.map(d => `<th>${d}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.map(week => `<tr>${week.map(cell => {
                                if (cell.other) {
                                    return `<td class='calendar-day calendar-day-other'></td>`;
                                } else {
                                    const isPast = cell.date < new Date(today.getFullYear(), today.getMonth(), today.getDate());
                                    const isSelected = selectedDate && cell.date.toDateString() === selectedDate.toDateString();
                                    return `<td class='calendar-day${isSelected ? ' calendar-day-selected' : ''}${isPast ? ' calendar-day-disabled' : ''}' data-date='${cell.date.toISOString().split('T')[0]}'>${cell.day}</td>`;
                                }
                            }).join('')}</tr>`).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            <button class="btn btn-outline calendar-cancel-btn" id="cancelCalendarBtn">Отмена</button>
        `;
    }

    setupEventHandlers() {
        const today = new Date();
        let currentMonth = this.stateManager.getState('selectedCalendarMonth') !== undefined ? this.stateManager.getState('selectedCalendarMonth') : today.getMonth();
        let currentYear = this.stateManager.getState('selectedCalendarYear') !== undefined ? this.stateManager.getState('selectedCalendarYear') : today.getFullYear();

        // Переключение месяцев
        const prevMonthBtn = document.getElementById('prevMonthBtn');
        const nextMonthBtn = document.getElementById('nextMonthBtn');
        
        if (prevMonthBtn) {
            prevMonthBtn.addEventListener('click', () => {
                if (currentMonth === 0) {
                    currentMonth = 11;
                    currentYear--;
                } else {
                    currentMonth--;
                }
                this.stateManager.setState('selectedCalendarMonth', currentMonth);
                this.stateManager.setState('selectedCalendarYear', currentYear);
                window.router.navigate('dateSelection');
            });
        }
        
        if (nextMonthBtn) {
            nextMonthBtn.addEventListener('click', () => {
                if (currentMonth === 11) {
                    currentMonth = 0;
                    currentYear++;
                } else {
                    currentMonth++;
                }
                this.stateManager.setState('selectedCalendarMonth', currentMonth);
                this.stateManager.setState('selectedCalendarYear', currentYear);
                window.router.navigate('dateSelection');
            });
        }

        // Выбор дня
        document.querySelectorAll('.calendar-day').forEach(cell => {
            if (!cell.classList.contains('disabled')) {
                cell.addEventListener('click', () => {
                    const selectedDate = cell.getAttribute('data-date');
                    const rangeMode = this.stateManager.getState('_calendarRangeMode');
                    if (rangeMode === 'to') {
                        this.stateManager.setState('selectedDateTo', selectedDate);
                    } else if (rangeMode === 'from') {
                        this.stateManager.setState('selectedDateFrom', selectedDate);
                    } else {
                        this.stateManager.setSelectedDate(selectedDate);
                    }
                    this.stateManager.setState('selectedCalendarMonth', undefined);
                    this.stateManager.setState('selectedCalendarYear', undefined);
                    
                    const previousScreen = this.stateManager.getPreviousScreen();
                    if (previousScreen) {
                        window.router.navigate(previousScreen);
                    } else {
                        window.router.navigate('findRide');
                    }
                });
            }
        });

        // Быстрый выбор "Сегодня" и "Завтра"
        const quickTodayBtn = document.getElementById('quickTodayBtn');
        const quickTomorrowBtn = document.getElementById('quickTomorrowBtn');
        
        if (quickTodayBtn) {
            quickTodayBtn.addEventListener('click', () => {
                const iso = today.toISOString().split('T')[0];
                this.stateManager.setSelectedDate(iso);
                this.stateManager.setState('selectedCalendarMonth', undefined);
                this.stateManager.setState('selectedCalendarYear', undefined);
                const previousScreen = this.stateManager.getPreviousScreen();
                if (previousScreen) {
                    window.router.navigate(previousScreen);
                } else {
                    window.router.navigate('findRide');
                }
            });
        }
        
        if (quickTomorrowBtn) {
            quickTomorrowBtn.addEventListener('click', () => {
                const tomorrow = new Date(today);
                tomorrow.setDate(today.getDate() + 1);
                const iso = tomorrow.toISOString().split('T')[0];
                this.stateManager.setSelectedDate(iso);
                this.stateManager.setState('selectedCalendarMonth', undefined);
                this.stateManager.setState('selectedCalendarYear', undefined);
                const previousScreen = this.stateManager.getPreviousScreen();
                if (previousScreen) {
                    window.router.navigate(previousScreen);
                } else {
                    window.router.navigate('findRide');
                }
            });
        }

        // Кнопка отмены
        const cancelBtn = document.getElementById('cancelCalendarBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                const previousScreen = this.stateManager.getPreviousScreen();
                if (previousScreen) {
                    window.router.navigate(previousScreen);
                } else {
                    window.router.navigate('findRide');
                }
            });
        }

        // Свайпы для смены месяца (только для мобильных)
        const cardBody = document.querySelector('.card-body');
        if (cardBody) {
            let touchStartX = null;
            cardBody.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    touchStartX = e.touches[0].clientX;
                }
            });
            cardBody.addEventListener('touchend', (e) => {
                if (touchStartX !== null && e.changedTouches.length === 1) {
                    const dx = e.changedTouches[0].clientX - touchStartX;
                    if (Math.abs(dx) > 40) {
                        if (dx < 0) {
                            // свайп влево — следующий месяц
                            document.getElementById('nextMonthBtn')?.click();
                        } else {
                            // свайп вправо — предыдущий месяц
                            document.getElementById('prevMonthBtn')?.click();
                        }
                    }
                }
                touchStartX = null;
            });
        }

        // Прокрутка к выбранной дате
        setTimeout(() => {
            const selected = document.querySelector('.calendar-day-selected');
            if (selected && selected.scrollIntoView) {
                selected.scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'});
            }
        }, 50);
    }
}

class TimeSelectionScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        const times = [];
        for (let hour = 6; hour <= 23; hour++) {
            for (let minute = 0; minute < 60; minute += 30) {
                const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                times.push(time);
            }
        }
        
        return `
            <h2 class="section-title">Выберите время</h2>
            
            <div class="card">
                <div class="card-body">
                    ${times.map(time => `
                        <div class="list-item time-item" data-time="${time}">
                            <div style="font-weight: 500;">${time}</div>
                            <i class="fas fa-chevron-right" style="color: #5f6368;"></i>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        document.querySelectorAll('.time-item').forEach(item => {
            item.addEventListener('click', () => {
                const selectedTime = item.getAttribute('data-time');
                this.stateManager.setSelectedTime(selectedTime);
                
                // Обновляем поле времени в предыдущем экране
                const previousScreen = this.stateManager.getPreviousScreen();
                if (previousScreen === 'createRide') {
                    const timeInput = document.getElementById('createTimeInput');
                    if (timeInput) {
                        timeInput.value = selectedTime;
                    }
                }
                
                // Возвращаемся к предыдущему экрану
                if (previousScreen) {
                    window.router.navigate(previousScreen);
                } else {
                    window.router.navigate('findRide');
                }
            });
        });
    }
}

export { DateSelectionScreen, TimeSelectionScreen };
export default DateSelectionScreen;
