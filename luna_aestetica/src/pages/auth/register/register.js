/* src/pages/auth/register/register.js */
import { IRouter } from '@aurelia/router'
import { resolve } from '@aurelia/kernel'
import { ApiService } from '@/services/api-service'

export default class Register {
  router = resolve(IRouter)
  api = resolve(ApiService)

  isLoading = false
  showPassword = false
  
  user = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: ''
  }

  async onRegister() {
  
    this.isLoading = true
    
    try {
   
      const payload = {
        username: this.user.email,
        email: this.user.email,
        password: this.user.password,
        first_name: this.user.first_name,
        last_name: this.user.last_name,
        phone: this.user.phone
      }
  
      await this.api.register(payload)
      alert("Registrazione avvenuta! Ora effettua il login.")
      this.router.load('login')
    } 
    catch (e) {
    
      const msg = e.username ? "Questo utente esiste già" : "Errore nella registrazione"
      alert(msg)
    } 
    finally {
    
      this.isLoading = false
    }
  }
}