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

  async conferma() {
  
    console.debug("Slot:", this.slotSelezionato, "Data:", this.dataSelezionata);
  
    if (!this.slotSelezionato || !this.dataSelezionata || this.carrello.length === 0) {
  
      alert("Dati incompleti! Seleziona servizi, data e orario.")
      return
    }
      
    const payload = {      
      service_ids: this.carrello.map(s => s.id),
      date: this.dataSelezionata,
      start_time: this.slotSelezionato.ora
    }
  
    console.log("Payload finale inviato:", payload)
    
    if (!payload.service_ids || payload.service_ids.length === 0 || !payload.date || !payload.start_time) {

      console.error("Payload non valido:", payload)
      alert("Errore nella preparazione dei dati.")
      return
    }
  
    try {

      const res = await this.api.salvaPrenotazione(payload);

      if (res) {
      
        alert("Prenotazione confermata!")
        this.router.load('home')
      }
    } 
    catch (e) {
    
      console.error("Errore salvataggio:", e)
      alert("Errore durante la prenotazione: " + e.message)
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
    
    return this.carrello.reduce((acc, s) => acc + (s.duration_minutes || 0), 0)
  }

  get carrello() {
  
    return this.servizi.filter(s => s.selected)
  }


  isSelezionato(id) {
  
    return this.carrello.some(s => s.id === id)
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

  get prezzoTotale() {

    return this.carrello.reduce((acc, s) => acc + parseFloat(s.price || 0), 0).toFixed(2)
  }
}