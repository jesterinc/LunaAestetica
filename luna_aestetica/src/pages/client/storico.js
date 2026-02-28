/* src/pages/client/storico/storico.js */
import { resolve } from '@aurelia/kernel'
import { IRouter } from '@aurelia/router'
import { ApiService } from '@/services/api-service'

export default class Storico {
  api = resolve(ApiService)
  router = resolve(IRouter)

  prenotazioni = []
  settings = { show_prices: true }

  async attaching() {

    await this.caricaDati()
  }

  async caricaDati() {

    try {
    
      const data = await this.api.getMiePrenotazioni()
      this.prenotazioni = Array.isArray(data) ? data : (data?.results || [])
      setTimeout(() => {

        if (window.lucide) {

          window.lucide.createIcons()
        }
      }, 100);
    } 
    catch (e) {
    
      console.error("Errore nel caricamento storico:", e)
    }
  }

  formattaData(dataIso) {

    if (!dataIso) {

      return ''
    }

    return new Date(dataIso).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  }

  getBookingStatus(p) {
  
    if (p.is_cancelled || p.status_display === 'Cancellato') {
      
      return { 
        icon: 'fa-circle-xmark',
        class: 'status-cancelled', 
        tooltip: 'Annullato' 
      }
    }
    
    if (p.is_future) {
      
      return { 
        icon: 'fa-calendar-check',
        class: 'status-pending', 
        tooltip: 'In Arrivo' 
      }
    }
    
    return { 
      icon: 'fa-circle-check',
      class: 'status-confirmed', 
      tooltip: 'Concluso' 
    }
  }

  async annulla(id) {
    
    if (!confirm("Sei sicuro di voler annullare questa prenotazione?")) {

      return
    }

    try {
    
      await this.api.cancellaPrenotazione(id)
      await this.caricaDati()
    } 
    catch (e) {
    
      alert("Errore: " + e.message)
    }
  }

  cambia(id) {

    this.router.load(`/prenota/${id}`)
  }
}