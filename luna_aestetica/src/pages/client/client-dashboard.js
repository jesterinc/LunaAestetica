/* src/pages/client/dashboard/client-dashboard.js */
import { resolve } from '@aurelia/kernel'
import { IRouter } from '@aurelia/router'
import { AuthService } from '@/services/auth-service'
import { createIcons, icons } from 'lucide'

export default class ClientDashboard {
  router = resolve(IRouter)
  authService = resolve(AuthService)
  username = ""

  prenota() {
   
    this.router.load('/prenota')
  }

  async attaching() {

    this.username = this.authService.currentUser?.username || "Ospite"
    
    createIcons({
      icons: icons
    })
  }
}