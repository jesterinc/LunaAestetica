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

  async cancellaPrenotazione(id) {
  
    const response = await this.http.post(`meets/appointments/${id}/cancel/`)
    return response.ok
  }

  async createStripeCheckout(type, amount, appointmentIds = []) {

    const payload = { type, amount, appointment_ids: appointmentIds }

    const res = await this.http.post('payments/create-checkout-session/', JSON.stringify(payload))
    
    if (!res.ok) {

      const errorData = await res.json()
      throw new Error(errorData.error || "Errore creazione sessione")
    }
    
    return res.json()
  }

  async getClientConfig() {
  
    try {

      const response = await this.http.get('settings/client-config/')
      return response
    } 
    catch (e) {

      console.warn("Usando settaggi di default")
      return { show_prices: true, cancellation_limit_hours: 24 }
    }
  }
  
  async getDateDisponibili(durataParam) {
  
    const res = await this.http.get('offered/servizi/date_disponibili/')
    return res.ok ? res.json() : []
  }
  
  async getMiePrenotazioni() {
 
    const res = await this.http.get('meets/appointments/me/')
    return res.json()
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

  async getWalletStatus() {
  
    const res = await this.http.get('payments/wallet/')
    return res.ok ? res.json() : { balance: 0 }
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

  async salvaPrenotazione(payload) {
  
    console.log("Invio al server con token automatico:", payload)
    
    try {
    
      const response = await this.http.post('offered/servizi/prenota/', JSON.stringify(payload))
      
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
}
