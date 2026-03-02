/* src/pages/client/prenota.js */
import { IRouter } from '@aurelia/router'
import { resolve, IPlatform } from '@aurelia/kernel'
import { ApiService } from '@/services/api-service'

export class Prenota {
  router = resolve(IRouter)
  api = resolve(ApiService)
  platform = resolve(IPlatform)
  
  dataSelezionata = null
  dateAbilitate = []
  orariLiberi = []
  servizi = []
  servizioSelezionato = null
  slotSelezionato = null
  step = 1
  
  async binding() {
  
    try {

      const dati = await this.api.getServizi()
      this.servizi = dati.map(s => ({ 
        ...s, 
        selected: false, 
        duration_minutes: s.duration_minutes || s.duration || 0 // Fallback
      }))
  
      console.log("Servizi pronti:", this.servizi)
    } 
    catch (e) {
      
      console.error("Errore caricamento:", e)
    }
  }

  async caricaOrari() {
  
    console.log("DEBUG INVIO -> Data:", this.dataSelezionata, "Durata:", this.durataTotale);
  
    if (!this.dataSelezionata || !this.durataTotale || this.durataTotale === 0) {
      
      console.warn("Dati mancanti per caricare gli orari")
      this.orariLiberi = []
      return
    }
  
    this.isLoadingOrari = true
    this.slotSelezionato = null
  
    try {

      const risposta = await this.api.getOrariDisponibili(
        this.dataSelezionata,
        this.durataTotale
      )
      
      console.log("RISPOSTA SERVER:", risposta)
      this.orariLiberi = risposta
    } 
    catch (e) {
    
      console.error("Errore API orari:", e)
      this.orariLiberi = []
    } 
    finally {
    
      this.isLoadingOrari = false
    }
  }

  get carrello() {
  
    return this.servizi.filter(s => s.selected)
  }

  async conferma() {
  
    if (!this.slotSelezionato || !this.dataSelezionata || this.carrello.length === 0) {

      alert("Seleziona i servizi e l'orario!")
      return
    }
  
    const totaleCalcolato = parseFloat(this.prezzoTotale)
    const nomiServizi = this.carrello.map(s => s.name).join(", ")
    const payload = {      
      service_ids: this.carrello.map(s => s.id),
      date: this.dataSelezionata,
      start_time: this.slotSelezionato.ora
    }
  
    try {
     
      const res = await this.api.salvaPrenotazione(payload)

      if (res.id) {
    
        const response = await this.api.getClientConfig()
        const config = (response && typeof response.json === 'function') ? await response.json() : response

        console.debug("+++++ payment_policy", config.payment_policy)

        if (config.payment_policy != 'NONE') {

          const datiAppuntamento = {
              id: res.id,
              totalPrice: totaleCalcolato,
              serviceName: nomiServizi
          }
          sessionStorage.setItem('pending_appointment', JSON.stringify(datiAppuntamento))
          await this.router.load('client/wallet')
          return
        }
        await this.router.load('client-dashboard')
      }    
    } 
    catch (e) {
    
      console.error("Errore salvataggio:", e)    
      alert("Si è verificato un errore durante il salvataggio.")
    }
  }

  dataSelezionataChanged(newValue) {
    console.log("Cambio data rilevato:", newValue);
    if (newValue) {
      // Usiamo il microtask per assicurarci che il valore sia stabilizzato
      this.platform.taskQueue.queueTask(() => {
        this.caricaOrari();
      });
    }
  }

  get durataTotale() {
    
    return this.carrello.reduce((acc, s) => {
    
      const d = parseInt(s.duration_minutes || s.duration) || 0
      return acc + d
    }, 0)
  }

  isSelezionato(id) {
  
    return this.carrello.some(s => s.id === id)
  }

  get prezzoTotale() {
  
    const totale = this.carrello.reduce((acc, s) => {

      const p = parseFloat(s.price) || 0
      return acc + p
    }, 0)
    
    return totale.toFixed(2)
  }

  async selezionaServizio(servizio) {

    this.servizioSelezionato = servizio
    console.log("Servizio ID:", this.servizioSelezionato.id)

    try {
  
      const dateFromServer = await this.api.getDateDisponibili()
      console.log("Date scaricate dal server:", dateFromServer)
      this.dateAbilitate = dateFromServer
      this.step = 2
    }
    catch (e) {
    
      console.error("Errore nel caricamento date", e)
    }

    await this.caricaOrari()
  }

  staNelCarrello(id) {

    return this.carrello.some(s => s.id === id)
  }

  toggleServizio(servizio) {
   
    servizio.selected = !servizio.selected
    this.servizi = [...this.servizi]
    this.slotSelezionato = null
    if (this.dataSelezionata) {

      this.caricaOrari()
    }
  }

  async vaiAlCalendario() {
    if (this.carrello.length === 0) return;
  
    this.isLoading = true;
    this.dateAbilitate = []; // Reset per sicurezza
  
    try {
      // 1. Chiamata al server (usa la durata del carrello)
      const dateRicevute = await this.api.getDateDisponibili(this.durataTotale);
      
      // 2. Log di controllo: devono esserci date tipo ["2026-02-27", "2026-02-28"]
      console.log("DATE DA ABILITARE:", dateRicevute);
  
      // 3. Assegna i dati
      this.dateAbilitate = [...dateRicevute];
  
      // 4. CAMBIA STEP SOLO ORA
      this.step = 2;
    } catch (e) {
      console.error("Errore caricamento date:", e);
    } finally {
      this.isLoading = false;
    }
  }
}