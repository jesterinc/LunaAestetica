/* src/components/client-header.js */
import { IRouter } from '@aurelia/router'
import { resolve } from '@aurelia/kernel'

export class ClientHeader {
  router = resolve(IRouter)

  async vaiAlMenu() {

    console.log("Tentativo di navigazione verso la dashboard...")
    await this.router.load('/client-dashboard')
  }

  logout() {
    
    localStorage.removeItem('token')
    this.router.load('login')
  }
}