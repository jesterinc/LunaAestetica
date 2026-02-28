/* src/pages/auth/login/login.js */
import { resolve } from '@aurelia/kernel'
import { IRouter } from '@aurelia/router'
import { AuthService } from '@/services/auth-service'

export default class Login {

  authService = resolve(AuthService)
  router = resolve(IRouter);

  username = ''
  password = ''
  errorMessage = ''

  vaiARegister() {

    this.router.load('register')
  }

  async submitLogin() {
  
    this.isLoading = true
    
    const result = await this.authService.login({
      username: this.username,
      password: this.password
    })

    if (result.success) {
      
      await this.router.load('client-dashboard')
    } 
    else {
    
      this.errorMessage = result.error
      alert(this.errorMessage)
    }
    
    this.isLoading = false
  }
}


