/* src/my-app.js */
import { IRouter } from '@aurelia/router'
import { resolve } from '@aurelia/kernel'

export class MyApp {

  router = resolve(IRouter)

  static routes = [
    { 
      path: ['', 'login'], 
      component: () => import('./pages/auth/login/login.js').then(m => m.default || m.Login), 
      title: 'Login' 
    },
    { 
      path: 'register', 
      component: () => import('./pages/auth/register/register.js').then(m => m.default || m.Register), 
      title: 'Registrati',
      id: 'register'
    },
    //{ 
    //  path: 'recover', 
    //  component: () => import('./pages/auth/recover/recover').then(m => m.default || m.Recover), 
    //  title: 'Recupero Password' 
    //},
    { 
      path: 'client-dashboard', 
      component: () => import('./pages/client/client-dashboard.js').then(m => m.default || m.ClientDashboard), 
      title: 'Dashboard cliente',
      id: 'client-dashboard'
    },
    { 
      path: 'prenota', 
      component: () => import('./pages/client/prenota.js').then(m => m.Prenota || m.default),
      title: 'Prenota',
      id: 'prenota' 
    },
    { 
      path: 'wallet', 
      component: () => import('./pages/client/wallet.js').then(m => m.Wallet || m.default),
      title: 'Wallet',
      id: 'wallet' 
    },
    { 
      path: 'storico', 
      component: () => import('./pages/client/storico.js').then(m => m.default || m.Storico),
      title: 'Storico prenotazioni cliente',
      id: 'storico'
    },
    //{ 
    //  path: 'admin-dashboard', 
    //  component: () => import('./pages/admin/dashboard/admin-dashboard').then(m => m.default || m.AdminDashboard),
    //  title: 'Dashboard amministratore'
    //},
  ]

  static isAuthenticated() {
  
    const token = localStorage.getItem('auth_token')
    return !!token || 'login'
  }

  static isAdmin() {

    // TODO: Put here a control of token or a state variable
    const isAdmin = localStorage.getItem('is_admin') === 'true'
    return (this.isAuthenticated() === true && isAdmin) || 'login'
  }

  get isAuthPage() {
   
    const path = this.router.activeNavigation?.instruction
    return ['login', 'register', 'recover', ''].includes(path)
  }
}
