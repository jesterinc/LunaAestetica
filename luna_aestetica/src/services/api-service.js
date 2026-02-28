/* src/services/api-service.js */
import { IHttpClient } from '@aurelia/fetch-client'
import { resolve } from '@aurelia/kernel'

export class ApiService {
  http = resolve(IHttpClient)

  constructor() {
    
    this.http.configure(config => {
      
      config.withInterceptor({
        request(request) {
        
          const token = localStorage.getItem('auth_token')
        
          if (token) {
        
            request.headers.append('Authorization', `Token ${token}`)
          }
        
          if (!request.headers.has('Content-Type')) {
        
            request.headers.append('Content-Type', 'application/json')
          }
        
          return request
        }
      })
    })
  }

  async getDateDisponibili(durataParam) {
  
    const res = await this.http.get('offered/servizi/date_disponibili/')
    return res.ok ? res.json() : []
  }
  
  async getOrariDisponibili(data, durata) {
  
    const url = `offered/servizi/orari_disponibili/?data=${data}&durata=${durata}`
    try {
  
      const response = await this.http.get(url)
  
      if (!response.ok) {

        throw new Error("Errore API orari")
      }

      return await response.json()
    } 
    catch (e) {
    
      console.error("Errore nel service orari:", e)
      throw e
    }
  }

  async getMiePrenotazioni() {
    
    await new Promise(r => setTimeout(r, 500))
    return [
      {
        servizio_nome: "Massaggio Decontratturante",
        data: "2026-10-12",
        ora_inizio: "14:30",
        stato_codice: "CONF",
        stato_testo: "Confermato"
      }
    ]
  }

  async getOrariLiberi(data, servizioId) {

    const res = await this.http.get(`prenotazioni/orari_liberi/?data=${data}&servizio_id=${servizioId}`)
    return res.ok ? res.json() : []
  }

  async getProfile() {

    const res = await this.http.get('auth/me/')
    return res.ok ? res.json() : null
  }

  async getServizi() {
  
    const res = await this.http.get('offered/servizi/')
    return res.ok ? res.json() : []
  }

  async salvaPrenotazione(payload) {
  
    console.log("Invio al server con token automatico:", payload)
    
    try {
    
      const response = await this.http.post('offered/servizi/prenota/', JSON.stringify(payload));
      
      if (!response.ok) {

        const errorData = await response.json()
        throw new Error(errorData.detail || "Errore nel salvataggio")
      }

      return await response.json()
    } 
    catch (e) {
    
      console.error("Errore API salvaPrenotazione:", e)
      throw e
    }
  }

  async register(userData) {
    
    try {
    
      const response = await this.http.post('auth/register/', JSON.stringify(userData), {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()
  
      if (!response.ok) {

        throw data
      }
  
      return data
    } 
    catch (e) {

      console.error("Errore API Register:", e)
      throw e
    }
  }
}