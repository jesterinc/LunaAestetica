/* src/pages/client/wallet.js */
/* src/pages/client/wallet.js */
import { IRouter } from '@aurelia/router'
import { resolve } from '@aurelia/kernel'
import { ApiService } from '../../services/api-service'

export class Wallet {
    api = resolve(ApiService)
    router = resolve(IRouter)

    appointment = { serviceName: "Servizio Luna AEstetica", amountToPay: 0, totalPrice: 0, id: null }
    errorMessage = ""
    isProcessing = false
    showReservationPay = true
    showWallet = true

    async loading() {
        console.log("Wallet in caricamento...")
        await this.loadInitialData()
    }

    async loadInitialData() {
        try {
            const storedData = sessionStorage.getItem('pending_appointment')
            if (!storedData) return

            const data = JSON.parse(storedData)
            this.appointment.id = data.id
            this.appointment.totalPrice = parseFloat(data.totalPrice) || 0
            this.appointment.serviceName = data.serviceName

            const response = await this.api.getClientConfig()
            const config = await response.json()

            if (this.appointment.totalPrice > 0 && config) {
                const p_in_cents = Math.round(this.appointment.totalPrice * 100)
                const policy = config.payment_policy
                const config_amount = parseFloat(config.payment_amount) || 0

                if (policy === 'PARTIAL') {
                    this.appointment.amountToPay = Math.round((p_in_cents * config_amount) / 100)
                } else if (policy === 'FULL') {
                    this.appointment.amountToPay = p_in_cents
                }

                if (this.appointment.amountToPay > 0) {
                    await this.executeStripeRedirect('APPOINTMENT', this.appointment.amountToPay, [this.appointment.id])
                }
            }
        } catch (e) {
            console.error("❌ Errore durante il caricamento iniziale:", e)
        }
    }

    // NUOVO METODO UNIFICATO PER IL REDIRECT
    async executeStripeRedirect(type, amountInCents, appointmentIds = []) {
        this.isProcessing = true
        try {
            console.log(`🚀 Avvio redirect Stripe per ${type}...`, { amountInCents })
            const session = await this.api.createStripeCheckout(type, amountInCents, appointmentIds)

            if (session && session.url) {
                // Puliamo la sessione solo se è un appuntamento
                if (type === 'APPOINTMENT') {
                    sessionStorage.removeItem('pending_appointment')
                }
                window.location.href = session.url
            } else {
                throw new Error("Il server non ha restituito un URL di pagamento valido.")
            }
        } catch (e) {
            console.error("❌ Errore Stripe:", e)
            alert("Errore durante l'avvio del pagamento: " + e.message)
        } finally {
            this.isProcessing = false
        }
    }

    // AGGIORNATO: Ora la ricarica usa il redirect
    selectTopup(amount) {
        const amountInCents = Math.round(amount * 100)
        this.executeStripeRedirect('WALLET_RELOAD', amountInCents, [])
    }
}
