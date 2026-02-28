/* src/components/custom-calendar.js */
import { bindable, BindingMode, inject } from 'aurelia';

@inject(Element)
export class CustomCalendar {
  @bindable({ mode: BindingMode.twoWay }) selectedDate;
  @bindable enabledDates = [];

  constructor(element) {
    this.element = element;
    this.viewDate = new Date();
    this.days = [];
    this.monthNames = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"];
  }

  // Scatta quando le date vengono caricate dal server
  enabledDatesChanged() {
    this.render();
  }

  // Scatta quando selezioni una data (per aggiornare la classe 'isSelected')
  selectedDateChanged() {
    this.render();
  }

  binding() {
    this.render();
  }

  render() {
    const year = this.viewDate.getFullYear();
    const month = this.viewDate.getMonth();
    
    // Calcolo giorni del mese e offset (Lunedì come primo giorno)
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const calendarDays = [];
    const offset = firstDay === 0 ? 6 : firstDay - 1;

    // Slot vuoti per i giorni del mese precedente
    for (let i = 0; i < offset; i++) {
      calendarDays.push({ day: null, isEnabled: false });
    }

    // Creazione set di confronto rapido (evita problemi di spazi o formati)
    const normalizedEnabled = (this.enabledDates || []).map(d => 
      String(typeof d === 'object' ? d.date : d).trim()
    );

    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      
      const isEnabled = normalizedEnabled.includes(dateStr);

      calendarDays.push({
        day: d,
        date: dateStr,
        isEnabled: isEnabled,
        isSelected: this.selectedDate === dateStr
      });
    }

    this.days = calendarDays;
  }

  select(dateObj) {
    if (dateObj.day && dateObj.isEnabled) {
      this.selectedDate = dateObj.date;
      
      // Notifichiamo il genitore (Prenota) che la data è cambiata
      this.element.dispatchEvent(new CustomEvent('change', {
        bubbles: true,
        detail: { value: this.selectedDate }
      }));
    }
  }

  prevMonth() {
    this.viewDate = new Date(this.viewDate.getFullYear(), this.viewDate.getMonth() - 1, 1);
    this.render();
  }

  nextMonth() {
    this.viewDate = new Date(this.viewDate.getFullYear(), this.viewDate.getMonth() + 1, 1);
    this.render();
  }
}