/* src/services/auth-service.js */
import { resolve } from '@aurelia/kernel';
import { IHttpClient } from '@aurelia/fetch-client';
import { ApiService } from './api-service';

export class AuthService {
  api = resolve(ApiService)
  http = resolve(IHttpClient)

  async login(credentials) {

    try {

      const response = await this.http.post('auth/login/', JSON.stringify(credentials), {
        headers: { 'Content-Type': 'application/json' }
      })

      const data = await response.json()

      if (!response.ok) {

        return { success: false, error: data.error || 'Credenziali errate' }
      }

      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('username', data.username)
      
      return { success: true, user: data }
    } 
    catch (e) {
    
      console.error("Errore nel Service Login:", e)
      return { success: false, error: "Errore di connessione al server" }
    }
  }

  async resolveLogin(credentials) {
  
    return this.login(credentials)
  }

  logout() {

    localStorage.removeItem('auth_token')
    localStorage.removeItem('username')
  }
}